from datetime import date, datetime
from typing import Any, Callable, Dict, List, Tuple

from sqlalchemy import Date, and_, cast, desc, label, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from sqlalchemy import distinct

from app.core.settings import get_settings
from app.model.alert_policy import AlertPolicy
from app.model.alert_policy_violations import AlertPolicyViolation
from app.model.asset import Asset
from app.model.asset_operator_assignment import AssetOperatorAssignment
from app.model.device import Device
from app.model.driver import Driver
from app.model.inventory import Inventory
from app.model.maintenance_alert import MaintenanceAlert
from app.model.tracking_event import TrackingEvent
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.asset_schema import AssignDeviceInputPayload
from app.util.enums import AssetCreators, AssetStatus
from app.util.utils import get_status
from app.model.buildings import Building


class AssetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Asset)

    async def read_all_assets_by_uuid_no_pagination(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        asset_uuid: str = None,
        asset_type_uuid: str = None,
    ):
        async with self.session_factory() as session:
            query = select(self.model)

            if asset_uuid:
                query = query.filter(self.model.uuid == asset_uuid)
            elif user_uuid:
                query = query.filter(self.model.user_uuid == user_uuid)
                if asset_type_uuid:
                    query = query.filter(self.model.asset_type_uuid == asset_type_uuid)
            elif business_uuid:
                query = query.filter(self.model.business_profile_uuid == business_uuid)
                if asset_type_uuid:
                    query = query.filter(self.model.asset_type_uuid == asset_type_uuid)

            result = await session.execute(query)
            return result.scalars().all()

    async def read_all_assets_by_uuid(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        asset_type_uuid: str = None,
        page: int = 1,
        page_size: int = 10,
        search_query: str = None,
        status: str = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Base query with necessary joins
            base_query = (
                select(self.model)
                .join(
                    AssetOperatorAssignment,
                    AssetOperatorAssignment.asset_uuid == self.model.uuid,
                    isouter=True,
                )
                .join(
                    User,
                    User.uuid == AssetOperatorAssignment.operator_uuid,
                    isouter=True,
                )
                .options(joinedload(self.model.alert_policies))
            )

            # Apply filters
            if user_uuid:
                base_query = base_query.filter(self.model.user_uuid == user_uuid)

            if business_uuid:
                base_query = base_query.filter(
                    self.model.business_profile_uuid == business_uuid
                )

            if asset_type_uuid:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            if search_query:
                base_query = base_query.filter(
                    or_(
                        self.model.asset_name.ilike(f"%{search_query}%"),
                        self.model.vehicle_license_no.ilike(f"%{search_query}%"),
                        self.model.vin.ilike(f"%{search_query}%"),
                        User.first_name.ilike(f"%{search_query}%"),
                        User.last_name.ilike(f"%{search_query}%"),
                    )
                )
            # Ensure only one DISTINCT is applied
            distinct_assets_query = base_query.with_only_columns(
                self.model.uuid
            ).distinct()

            # Now, correctly count the distinct assets
            total_assets_stmt = select(func.count()).select_from(
                distinct_assets_query.subquery()
            )

            total_assets_result = await session.execute(total_assets_stmt)
            total_assets = total_assets_result.scalar()

            # Calculate total pages
            total_pages = (total_assets + page_size - 1) // page_size

            # Apply ordering, pagination, and relationships loading
            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.asset_type))
                .options(
                    joinedload(self.model.device)
                    .joinedload(Device.inventory)
                    .joinedload(Inventory.images)
                )
                .options(joinedload(self.model.equipment))
            )

            result = await session.execute(paginated_query)
            assets = result.unique().scalars().all()

            # Process assets (including operator info and tracking event)
            processed_assets = await self.process_assets(session, assets)

            # Filter by status if provided
            asset_data = [
                asset
                for asset in processed_assets
                if not status
                or (
                    asset.device_imei
                    and asset.last_tracking_event.get("status") == status
                )
            ]

            # Get asset status counts
            moving_asset_count, idle_asset_count, stopped_asset_count = (
                self.get_asset_status_counts(asset_data)
            )

            return {
                "assets": asset_data,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "moving_assets": moving_asset_count,
                "idle_assets": idle_asset_count,
                "stopped_assets": stopped_asset_count,
            }

    async def read_vehicle_building_assets_by_business_uuid(
        self,
        business_uuid: str,
        operator_uuid: str = None,
        search_query: str = None,
        asset_type_uuid: str = None,
        status: str = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            all_asset_data = []

            # Fetch vehicle assets
            vehicle_stmt = (
                select(self.model)
                .join(
                    AssetOperatorAssignment,
                    AssetOperatorAssignment.asset_uuid == self.model.uuid,
                    isouter=True,
                )
                .options(joinedload(self.model.asset_type))
                .filter(self.model.business_profile_uuid == business_uuid)
            )

            if operator_uuid:
                vehicle_stmt = vehicle_stmt.filter(
                    AssetOperatorAssignment.operator_uuid == operator_uuid
                )

            vehicle_result = await session.execute(vehicle_stmt)
            vehicle_assets = vehicle_result.unique().scalars().all()

            # Process vehicle assets
            processed_vehicle_assets = await self.process_assets(
                session, vehicle_assets
            )

            for vehicle_asset in processed_vehicle_assets:
                last_tracking_event = getattr(
                    vehicle_asset, "last_tracking_event", None
                )
                if vehicle_asset.device_imei:
                    all_asset_data.append(
                        {
                            "uuid": vehicle_asset.uuid,
                            "asset_name": vehicle_asset.asset_name,
                            "marker_icon_color": vehicle_asset.marker_color,
                            "status": (
                                last_tracking_event.get("status")
                                if last_tracking_event
                                else "unknown"
                            ),
                            "last_tracking_event": {
                                "lng": (
                                    last_tracking_event.get("lng", None)
                                    if last_tracking_event
                                    else None
                                ),
                                "lat": (
                                    last_tracking_event.get("lat", None)
                                    if last_tracking_event
                                    else None
                                ),
                            },
                            "operator": vehicle_asset.operator,
                            "asset_type": {
                                "uuid": vehicle_asset.asset_type.uuid,
                                "asset_type_name": vehicle_asset.asset_type.asset_type_name,
                                "status": vehicle_asset.asset_type.status,
                                "created_at": vehicle_asset.asset_type.created_at,
                            },
                        }
                    )

            # Fetch and process building assets if operator_uuid is null
            if not operator_uuid:
                building_stmt = (
                    select(Building)
                    .options(joinedload(Building.asset_type))
                    .filter(Building.business_profile_uuid == business_uuid)
                )
                building_result = await session.execute(building_stmt)
                building_assets = building_result.unique().scalars().all()

                for building_asset in building_assets:
                    all_asset_data.append(
                        {
                            "uuid": building_asset.uuid,
                            "asset_name": building_asset.building_name,
                            "marker_icon_color": None,
                            "status": getattr(building_asset, "status", "unknown"),
                            "last_tracking_event": {
                                "lng": building_asset.longitude,
                                "lat": building_asset.latitude,
                            },
                            "operator": None,
                            "asset_type": {
                                "uuid": building_asset.asset_type.uuid,
                                "asset_type_name": building_asset.asset_type.asset_type_name,
                                "status": building_asset.asset_type.status,
                                "created_at": building_asset.asset_type.created_at,
                            },
                        }
                    )

            # Apply status filter
            if status:
                all_asset_data = [
                    asset for asset in all_asset_data if asset["status"] == status
                ]

            # Apply search filter
            if search_query:
                all_asset_data = [
                    asset
                    for asset in all_asset_data
                    if search_query.lower() in asset["asset_name"].lower()
                ]

            if asset_type_uuid:
                all_asset_data = [
                    asset
                    for asset in all_asset_data
                    if str(asset["asset_type"]["uuid"]) == asset_type_uuid
                ]

            return {"assets": all_asset_data}

    def get_asset_status_counts(self, assets: List[Any]) -> Tuple[int, int, int]:
        moving_asset_count = 0
        idle_asset_count = 0
        stopped_asset_count = 0

        for asset in assets:
            if hasattr(asset, "last_tracking_event") and asset.last_tracking_event:
                tracking_event = asset.last_tracking_event
                event_type = str(tracking_event.get("event_type", "unknown"))

                status = get_status(event_type)

                if status == "moving":
                    moving_asset_count += 1
                elif status == "idle":
                    idle_asset_count += 1
                else:
                    stopped_asset_count += 1  # Count unknown statuses as stopped
            else:
                stopped_asset_count += 1  # No tracking event, count as stopped

        return moving_asset_count, idle_asset_count, stopped_asset_count

    async def read_assigned_assets_by_uuid(
        self,
        operator_uuid: str,
        business_uuid: str = None,
        asset_type_uuid: str = None,
        page: int = 1,
        page_size: int = 10,
        search_query: str = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Base query with joins
            base_query = (
                select(self.model).join(
                    AssetOperatorAssignment,
                    AssetOperatorAssignment.asset_uuid == self.model.uuid,
                )
                # .options(joinedload(self.model.alert_policies))
                .filter(AssetOperatorAssignment.operator_uuid == operator_uuid)
            )

            # Apply filters
            if business_uuid:
                base_query = base_query.filter(
                    self.model.business_profile_uuid == business_uuid
                )

            if asset_type_uuid:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            if search_query:
                base_query = base_query.filter(
                    or_(
                        self.model.asset_name.ilike(f"%{search_query}%"),
                        self.model.vehicle_license_no.ilike(f"%{search_query}%"),
                        self.model.vin.ilike(f"%{search_query}%"),
                        User.first_name.ilike(f"%{search_query}%"),
                        User.last_name.ilike(f"%{search_query}%"),
                    )
                )

            # Get total assets count
            total_assets_stmt = select(func.count()).select_from(base_query.subquery())
            total_assets_result = await session.execute(total_assets_stmt)
            total_assets = total_assets_result.scalar()

            # Calculate total pages
            total_pages = (total_assets + page_size - 1) // page_size

            # Apply ordering, pagination, and relationships loading
            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.asset_type))
                .options(joinedload(self.model.device).joinedload(Device.inventory))
                .options(joinedload(self.model.equipment))
            )

            result = await session.execute(paginated_query)
            assets = result.scalars().all()

            # Process assets (including operator info and tracking event)
            processed_assets = await self.process_assets(session, assets)

            # Get asset status counts
            moving_asset_count, idle_asset_count, stopped_asset_count = (
                self.get_asset_status_counts(processed_assets)
            )

            return {
                "assets": processed_assets,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "moving_assets": moving_asset_count,
                "idle_assets": idle_asset_count,
                "stopped_assets": stopped_asset_count,
            }

    def get_asset_status_counts(self, assets: List[Any]) -> Tuple[int, int, int]:
        moving_asset_count = 0
        idle_asset_count = 0
        stopped_asset_count = 0

        for asset in assets:
            if (
                hasattr(asset, "last_tracking_event")
                and asset.last_tracking_event is not None
            ):
                tracking_event = asset.last_tracking_event
                if "event_type" in tracking_event:
                    if get_status(str(tracking_event["event_type"])) == "moving":
                        moving_asset_count += 1
                    elif get_status(str(tracking_event["event_type"])) == "idle":
                        idle_asset_count += 1
                    stopped_asset_count = len(assets) - (
                        moving_asset_count + idle_asset_count
                    )

        return moving_asset_count, idle_asset_count, stopped_asset_count

    async def process_assets(self, session, assets: List[Any]) -> List[Any]:
        for asset in assets:
            # Check if asset has device IMEI
            if asset.device_imei:
                # Get device's last known location
                result = await session.execute(
                    select(
                        label("lat", TrackingEvent.latitude),
                        label("lng", TrackingEvent.longitude),
                        TrackingEvent.speed,
                        TrackingEvent.course,
                        label("timestamp", TrackingEvent.event_datetime),
                        label("event_type", TrackingEvent.event_type),
                        label("fuel_level", TrackingEvent.fuel_level),
                    )
                    .filter(TrackingEvent.device_imei == asset.device_imei)
                    .order_by(desc(TrackingEvent.event_datetime))
                    .limit(1)
                )
                last_tracking_event = result.first()

                if last_tracking_event:
                    # Construct a dictionary with the retrieved fields
                    asset.last_tracking_event = {
                        "lat": last_tracking_event.lat,
                        "lng": last_tracking_event.lng,
                        "speed": last_tracking_event.speed,
                        "course": last_tracking_event.course,
                        "timestamp": last_tracking_event.timestamp,
                        "event_type": last_tracking_event.event_type,
                        "status": get_status(last_tracking_event.event_type),
                        "fuel_level": last_tracking_event.fuel_level,
                    }
                else:
                    asset.last_tracking_event = None

            # Fetch the assigned operator from AssetOperatorAssignment
            result = await session.execute(
                select(AssetOperatorAssignment.operator_uuid)
                .filter(AssetOperatorAssignment.asset_uuid == asset.uuid)
                .limit(1)
            )
            operator_assignment = result.scalar()

            if operator_assignment:
                # Fetch the operator (user) details
                result = await session.execute(
                    select(User).filter(User.uuid == operator_assignment).limit(1)
                )
                operator = result.scalars().first()

                if operator:
                    asset.operator = {
                        "uuid": operator.uuid,
                        "first_name": operator.first_name,
                        "last_name": operator.last_name,
                        "email": operator.email_address,
                        "image_url": operator.avatar_url,
                        "operator_type": operator.operator_type,
                        "phone_number": operator.phone_number,
                    }
                else:
                    asset.operator = None
            else:
                asset.operator = None

        return assets

    async def read_all_third_party_assets(
        self, asset_type_uuid: str = None, page=1, page_size=10
    ):
        async with self.session_factory() as session:
            # Calculate pagination offset
            offset = (page - 1) * page_size

            # Base Query
            base_query = select(self.model).filter(
                str(self.model.created_by) == AssetCreators.DVLA.value
            )

            # Apply asset type filter if provided
            if asset_type_uuid:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            # Count total records (before pagination)
            total_assets_query = select(func.count()).select_from(base_query.subquery())
            total_assets_result = await session.execute(total_assets_query)
            total_assets = total_assets_result.scalar()

            # Fetch paginated assets
            asset_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(
                    joinedload(Asset.asset_type),
                    joinedload(Asset.driver),
                    joinedload(Asset.device),
                    joinedload(Asset.equipment),
                    joinedload(Asset.vehicle_owner),
                )
            )

            assets_result = await session.execute(asset_query)
            assets = assets_result.scalars().all()

            return assets, total_assets

    async def read_all_stolen_assets(
        self, asset_type_uuid: str = None, page=1, page_size=10
    ):
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Base query: Get stolen assets
            base_query = select(self.model).filter(
                self.model.asset_stolen_status.is_(True)
            )

            # Apply asset type filter
            if asset_type_uuid:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            # Get total stolen assets count
            total_assets_stmt = select(func.count()).select_from(base_query.subquery())
            total_assets_result = await session.execute(total_assets_stmt)
            total_assets = total_assets_result.scalar()

            # Apply ordering, pagination, and relationship loading
            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.asset_type))
                .options(joinedload(self.model.driver))
                .options(joinedload(self.model.device))
                .options(joinedload(self.model.equipment))
                .options(joinedload(self.model.vehicle_owner))
            )

            result = await session.execute(paginated_query)
            assets = result.unique().scalars().all()

            # Batch fetch last tracking events for all assets with device_imei
            device_imeis = [asset.device_imei for asset in assets if asset.device_imei]
            tracking_events_dict = {}

            if device_imeis:
                tracking_stmt = (
                    select(
                        TrackingEvent.device_imei,
                        label("lat", TrackingEvent.latitude),
                        label("lng", TrackingEvent.longitude),
                        TrackingEvent.speed,
                        TrackingEvent.course,
                        label("timestamp", TrackingEvent.event_datetime),
                        label("event_type", TrackingEvent.event_type),
                    )
                    .where(TrackingEvent.device_imei.in_(device_imeis))
                    .order_by(desc(TrackingEvent.event_datetime))
                    .limit(len(device_imeis))  # Ensure we fetch one event per device
                )
                tracking_result = await session.execute(tracking_stmt)
                tracking_events = tracking_result.fetchall()

                for event in tracking_events:
                    tracking_events_dict[event.device_imei] = {
                        "lat": event.lat,
                        "lng": event.lng,
                        "speed": event.speed,
                        "course": event.course,
                        "timestamp": event.timestamp,
                        "event_type": event.event_type,
                    }

            # Assign last tracking events to assets
            for asset in assets:
                asset.last_tracking_event = tracking_events_dict.get(
                    asset.device_imei, None
                )

            return assets, total_assets

    async def assign_device_imei(
        self, asset_uuid, payload: AssignDeviceInputPayload
    ) -> Asset:
        async with self.session_factory() as session:
            # Fetch device by IMEI
            device_stmt = select(Device).filter(
                Device.device_imei == payload.device_imei
            )
            device_result = await session.execute(device_stmt)
            device = device_result.scalar()

            # Validate IMEI
            if not device:
                raise Exception(f"Device with IMEI {payload.device_imei} not found")

            # Check if device is already assigned
            if device.assign_to_asset_status is not None:
                raise Exception("Device already assigned to an asset")

            # Fetch asset by UUID
            asset_stmt = select(self.model).filter(self.model.uuid == asset_uuid)
            asset_result = await session.execute(asset_stmt)
            asset = asset_result.scalar()

            # Validate asset existence
            if not asset:
                raise Exception(f"Asset with ID {asset_uuid} not found")

            # Fetch user by asset user_uuid
            user_stmt = select(User).filter(User.uuid == asset.user_uuid)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar()

            if not user:
                raise Exception(f"User with UUID {asset.user_uuid} not found")

            # Update asset details
            asset.device_imei = payload.device_imei
            asset.asset_status = AssetStatus.ACTIVE

            # Update device details
            device.assign_to_asset_status = datetime.utcnow()
            device.user_uuid = user.uuid
            device.sim_phone_number = payload.sim_phone_number

            # Assign business UUID if applicable
            if user.business_profile_uuid:
                device.business_profile_uuid = user.business_profile_uuid

            # Commit all changes in a single transaction
            await session.commit()
            await session.refresh(asset)
            await session.refresh(device)

        return asset

    async def read_by_vin_serial_number_license_no(
        self, vin: str = None, serial_number: str = None, vehicle_license_no: str = None
    ):
        async with self.session_factory() as session:
            filters = []

            if vehicle_license_no:
                filters.append(self.model.vehicle_license_no == vehicle_license_no)
            if vin:
                filters.append(self.model.vin == vin)
            if serial_number:
                filters.append(self.model.serial_number == serial_number)

            if filters:
                stmt = select(self.model).filter(
                    or_(*filters)
                )  # Check all conditions in one query
                result = await session.execute(stmt)
                existing_asset = result.scalar()

                if existing_asset:
                    if existing_asset.vehicle_license_no == vehicle_license_no:
                        raise Exception(
                            "Asset with the given license number already exists."
                        )
                    if existing_asset.vin == vin:
                        raise Exception("Asset with the given VIN already exists.")
                    if existing_asset.serial_number == serial_number:
                        raise Exception(
                            "Asset with the given serial number already exists."
                        )

    async def update_asset_stolen_status_to_true(self, asset_uuid: str):
        async with self.session_factory() as session:
            # Fetch asset
            asset_stmt = select(self.model).filter(self.model.uuid == asset_uuid)
            asset_result = await session.execute(asset_stmt)
            asset = asset_result.scalar()

            # Check if asset exists
            if not asset:
                raise Exception(f"Asset with ID {asset_uuid} not found")

            # Update stolen status
            asset.asset_stolen_status = True

            # Commit and refresh
            await session.commit()
            await session.refresh(asset)

            return asset

    async def update_asset_stolen_status_to_false(self, asset_uuid: str):
        async with self.session_factory() as session:
            # Fetch asset
            asset_stmt = select(self.model).filter(self.model.uuid == asset_uuid)
            asset_result = await session.execute(asset_stmt)
            asset = asset_result.scalar()

            # Check if asset exists
            if not asset:
                raise Exception(f"Asset with ID {asset_uuid} not found")

            # Update stolen status
            asset.asset_stolen_status = False

            # Commit and refresh
            await session.commit()
            await session.refresh(asset)

            return asset

    async def get_over_speeding_violations(
        self,
        asset_uuid: str,
        alert_policy_type_uuid: str,
        start_date: str,
        end_date: str,
    ):
        async with self.session_factory() as session:
            query = (
                select(AlertPolicyViolation)
                .join(
                    AlertPolicy,
                    AlertPolicyViolation.alert_policy_uuid == AlertPolicy.uuid,
                )
                .filter(
                    AlertPolicyViolation.asset_uuid == asset_uuid,
                    AlertPolicy.alert_policy_type_uuid
                    == alert_policy_type_uuid.value,  # Ensure it's a string
                    and_(
                        cast(AlertPolicyViolation.created_at, Date)
                        >= datetime.strptime(start_date, "%d/%m/%Y").date(),
                        cast(AlertPolicyViolation.created_at, Date)
                        <= datetime.strptime(end_date, "%d/%m/%Y").date(),
                    ),
                )
            )

            result = await session.execute(query)
            return result.scalars().all()

    async def get_violations_by_alert_type(
        self,
        alert_policy_type_uuid: str,
        start_date: str,
        end_date: str,
        user_uuid: str = None,
        business_uuid: str = None,
        asset_uuid: str = None,
        asset_type_uuid: str = None,
    ):
        async with self.session_factory() as session:
            # Convert dates to datetime objects with timezone
            start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f %z")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f %z")
            base_query = (
                select(AlertPolicyViolation)
                .join(
                    AlertPolicy,
                    AlertPolicyViolation.alert_policy_uuid == AlertPolicy.uuid,
                )
                .filter(
                    AlertPolicy.alert_policy_type_uuid == alert_policy_type_uuid.value,
                    and_(
                        AlertPolicyViolation.created_at >= start_dt,
                        AlertPolicyViolation.created_at <= end_dt,
                    ),
                )
            )

            if user_uuid:
                base_query = base_query.filter(
                    AlertPolicyViolation.user_uuid == user_uuid
                )
            if business_uuid:
                base_query = base_query.filter(
                    AlertPolicyViolation.business_profile_uuid == business_uuid
                )
            if asset_uuid:
                base_query = base_query.filter(
                    AlertPolicyViolation.asset_uuid == asset_uuid
                )
            if asset_type_uuid:
                base_query = base_query.join(
                    Asset, AlertPolicyViolation.asset_uuid == Asset.uuid
                ).filter(Asset.asset_type_uuid == asset_type_uuid)
            result = await session.execute(base_query)
            return result.scalars().all()

    async def get_violations_by_asset(
        self,
        asset_uuid: str,
        start_date: str,
        end_date: str,
    ):
        async with self.session_factory() as session:
            date_from_obj = datetime.strptime(
                start_date, get_settings().DATE_FORMAT_YEAR
            ).date()
            date_to_obj = datetime.strptime(
                end_date, get_settings().DATE_FORMAT_YEAR
            ).date()

            # Define the query using `select()`
            stmt = (
                select(AlertPolicyViolation)
                .options(
                    joinedload(AlertPolicyViolation.alert_policy).joinedload(
                        AlertPolicy.alert_policy_type
                    ),
                    joinedload(AlertPolicyViolation.asset).joinedload(Asset.equipment),
                )
                .where(
                    AlertPolicyViolation.asset_uuid == asset_uuid,
                    and_(
                        cast(AlertPolicyViolation.created_at, date) >= date_from_obj,
                        cast(AlertPolicyViolation.created_at, date) <= date_to_obj,
                    ),
                )
            )

            # Execute the query asynchronously
            result = await session.execute(stmt)

            # Return the results as a list
            return result.scalars().all()

    async def get_asset_with_relationships(
        self, asset_uuid: str, date_from: str, date_to: str
    ):
        try:
            date_from_obj = datetime.strptime(
                date_from, get_settings().DATE_FORMAT_YEAR
            ).date()
            date_to_obj = datetime.strptime(
                date_to, get_settings().DATE_FORMAT_YEAR
            ).date()
        except ValueError as e:
            raise ValueError("Date format should be dd/mm/yyyy") from e

        async with self.session_factory() as session:
            # Fetch asset with relationships
            stmt = (
                select(self.model)
                .filter_by(uuid=asset_uuid)
                .options(
                    joinedload(self.model.asset_type),
                    joinedload(self.model.equipment),
                )
            )
            result = await session.execute(stmt)
            asset = result.unique().scalar()

            if asset and asset.device_imei:
                # Get device's tracking events within the specified date range
                tracking_stmt = (
                    select(
                        label("latitude", TrackingEvent.latitude),
                        label("longitude", TrackingEvent.longitude),
                        TrackingEvent.speed,
                        TrackingEvent.course,
                        label("timestamp", TrackingEvent.event_datetime),
                        label("event_type", TrackingEvent.event_type),
                        label("fuel_level", TrackingEvent.fuel_level),
                    )
                    .filter(
                        TrackingEvent.device_imei == asset.device_imei,
                        and_(
                            cast(TrackingEvent.event_datetime, Date) >= date_from_obj,
                            cast(TrackingEvent.event_datetime, Date) <= date_to_obj,
                        ),
                    )
                    .order_by(desc(TrackingEvent.event_datetime))
                )

                tracking_result = await session.execute(tracking_stmt)
                last_tracking_events = tracking_result.all()

                # Ensure last_tracking_events is a list of dictionaries
                asset.tracking_events = [
                    {
                        "latitude": event.latitude,
                        "longitude": event.longitude,
                        "speed": event.speed,
                        "course": event.course,
                        "timestamp": str(event.timestamp),
                        "event_type": get_status(event.event_type),
                        "fuel_level": event.fuel_level,
                    }
                    for event in last_tracking_events
                ]

            return asset

    async def get_maintenance_by_alert_type(
        self,
        alert_policy_type_uuid: str,
        maintenance_type_uuid: str,
        start_date: str,
        end_date: str,
        user_uuid: str = None,
        business_uuid: str = None,
        asset_uuid: str = None,
        asset_type_uuid: str = None,
    ):
        async with self.session_factory() as session:
            base_query = (
                select(MaintenanceAlert)
                .join(
                    AlertPolicy, MaintenanceAlert.alert_policy_uuid == AlertPolicy.uuid
                )
                .filter(
                    AlertPolicy.alert_policy_type_uuid == alert_policy_type_uuid.value,
                    AlertPolicy.maintenance_alert_type_uuid
                    == maintenance_type_uuid.value,
                    cast(MaintenanceAlert.created_at, Date)
                    >= datetime.strptime(start_date, "%d/%m/%Y"),
                    cast(MaintenanceAlert.created_at, Date)
                    <= datetime.strptime(end_date, "%d/%m/%Y"),
                )
            )

            if user_uuid:
                base_query = base_query.filter(MaintenanceAlert.user_uuid == user_uuid)
            if business_uuid:
                base_query = base_query.filter(
                    MaintenanceAlert.business_profile_uuid == business_uuid
                )
            if asset_uuid:
                base_query = base_query.filter(
                    MaintenanceAlert.asset_uuid == asset_uuid
                )
            if asset_type_uuid:
                base_query = base_query.join(
                    Asset, MaintenanceAlert.asset_uuid == Asset.uuid
                ).filter(Asset.asset_type_uuid == asset_type_uuid)

            result = await session.execute(base_query)
            return result.scalars().all()

    async def get_maintenance_by_asset(
        self, asset_uuid: str, start_date: str, end_date: str
    ):
        async with self.session_factory() as session:
            # Convert date strings to datetime objects
            start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
            end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")

            # Query using `select()` for async compatibility
            base_query = (
                select(MaintenanceAlert)
                .options(joinedload(MaintenanceAlert.alert_policy))
                .filter(
                    MaintenanceAlert.created_at.between(
                        start_date_obj, end_date_obj
                    ),  # Efficient date filtering
                    MaintenanceAlert.asset_uuid == asset_uuid,
                )
            )

            # Execute the query and fetch results
            maintenance_alerts_result = await session.execute(base_query)
            return maintenance_alerts_result.scalars().all()

    async def get_asset_by_user_uuid(self, user_uuid: str):
        async with self.session_factory() as session:
            asset_stmt = select(self.model).filter(self.model.user_uuid == user_uuid)
            result = await session.execute(asset_stmt)
            return result.scalar_one_or_none()

    async def get_asset_by_license_no(self, vehicle_license_no: str):
        async with self.session_factory() as session:
            asset_stmt = select(self.model).filter(
                self.model.vehicle_license_no == vehicle_license_no
            )
            result = await session.execute(asset_stmt)
            return result.scalar_one_or_none()

    async def get_driver_by_asset_uuid(self, asset_uuid: str):
        async with self.session_factory() as session:
            driver_stmt = select(Driver).filter(Driver.asset_uuid == asset_uuid)
            result = await session.execute(driver_stmt)
            return result.scalar_one_or_none()

    async def get_asset_by_driver_email(self, driver_email: str):
        async with self.session_factory() as session:
            asset_stmt = select(Asset).join(Driver).filter(Driver.email == driver_email)
            result = await session.execute(asset_stmt)
            return result.scalar_one_or_none()

    async def get_assets_by_imeis(self, imeis: List[str]):
        async with self.session_factory() as session:
            asset_stmt = select(Asset).filter(Asset.device_imei.in_(imeis))
            result = await session.execute(asset_stmt)
            return result.scalars().all()

    async def get_all_device_imeis(self):
        """Asynchronously retrieves all distinct device IMEIs from the Asset table."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Asset.device_imei)
                .where(Asset.device_imei.isnot(None))
                .distinct()
            )

            return [imei for (imei) in result.scalars().all()]
