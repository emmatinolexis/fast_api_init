from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple

from sqlalchemy import Date, and_, cast, desc, label, or_, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

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
            if user_uuid is not None:
                if asset_uuid:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.uuid == asset_uuid
                            )
                        )
                        .scalars()
                        .all()
                    )
                elif asset_type_uuid:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.user_uuid == user_uuid,
                                self.model.asset_type_uuid == asset_type_uuid,
                            )
                        )
                        .scalars()
                        .all()
                    )
                else:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.user_uuid == user_uuid
                            )
                        )
                        .scalars()
                        .all()
                    )

            if business_uuid is not None:
                if asset_uuid:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.uuid == asset_uuid
                            )
                        )
                        .scalars()
                        .all()
                    )
                elif asset_type_uuid:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.business_profile_uuid == business_uuid,
                                self.model.asset_type_uuid == asset_type_uuid,
                            )
                        )
                        .scalars()
                        .all()
                    )
                else:
                    return (
                        await session.execute(
                            session.query(self.model).filter(
                                self.model.business_profile_uuid == business_uuid
                            )
                        )
                        .scalars()
                        .all()
                    )

            return []

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
        page=1,
        page_size=10,
        search_query: str = None,
        status: str = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            # Calculate the offset based on the page and per_page values
            offset = (page - 1) * page_size

            # Start with a base query, apply joins here before limit and offset
            base_query = (
                session.query(self.model)
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
            )

            # Apply filters first before limit and offset
            if user_uuid is not None:
                base_query = base_query.filter(self.model.user_uuid == user_uuid)

            if business_uuid is not None:
                base_query = base_query.filter(
                    self.model.business_profile_uuid == business_uuid
                )

            if asset_type_uuid is not None:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            if search_query:
                base_query = base_query.filter(
                    or_(
                        self.model.asset_name.ilike(f"%{search_query}%"),
                        self.model.vehicle_license_no.ilike(f"%{search_query}%"),
                        self.model.vin.ilike(f"%{search_query}%"),
                        User.first_name.ilike(
                            f"%{search_query}%"
                        ),  # Search by operator's first name
                        User.last_name.ilike(f"%{search_query}%"),
                    )
                )

            # Query to get the total count of assets
            total_assets = await session.execute(base_query.count())
            total_assets = total_assets.scalar()

            # Calculate total pages
            total_pages = (total_assets + page_size - 1) // page_size

            # Apply ordering and pagination after filtering
            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = await session.execute(
                paginated_query.options(joinedload(self.model.asset_type))
                .options(
                    joinedload(self.model.device)
                    .joinedload(Device.inventory)
                    .joinedload(Inventory.images)
                )
                .options(joinedload(self.model.equipment))
            )
            assets = assets.unique().scalars().all()

            # Process assets (including operator info and tracking event)
            processed_assets = await self.process_assets(session, assets)
            asset_data = []

            if status:
                for asset in processed_assets:
                    if asset.device_imei:
                        if asset.last_tracking_event.get("status") == status:
                            asset_data.append(asset)
            else:
                asset_data = processed_assets

            # Get asset status counts (moving, idle, stopped)
            (
                moving_asset_count,
                idle_asset_count,
                stopped_asset_count,
            ) = self.get_asset_status_counts(asset_data)

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

            base_query = (
                session.query(self.model)
                .join(
                    AssetOperatorAssignment,
                    AssetOperatorAssignment.asset_uuid == self.model.uuid,
                )
                .filter(AssetOperatorAssignment.operator_uuid == operator_uuid)
            )

            if business_uuid is not None:
                base_query = base_query.filter(
                    self.model.business_profile_uuid == business_uuid
                )

            if asset_type_uuid is not None:
                base_query = base_query.filter(
                    self.model.asset_type_uuid == asset_type_uuid
                )

            if search_query:
                base_query = base_query.filter(
                    or_(
                        self.model.asset_name.ilike(f"%{search_query}%"),
                        self.model.vehicle_license_no.ilike(f"%{search_query}%"),
                        self.model.vin.ilike(f"%{search_query}%"),
                        User.first_name.ilike(
                            f"%{search_query}%"
                        ),  # Search by operator's first name
                        User.last_name.ilike(f"%{search_query}%"),
                    )
                )

            total_assets = await session.execute(base_query.count())
            total_assets = total_assets.scalar()
            total_pages = (total_assets + page_size - 1) // page_size

            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = await session.execute(
                paginated_query.options(joinedload(self.model.asset_type))
                .options(joinedload(self.model.device).joinedload(Device.inventory))
                .options(joinedload(self.model.equipment))
            )
            assets = assets.unique().scalars().all()

            processed_assets = await self.process_assets(session, assets)

            (
                moving_asset_count,
                idle_asset_count,
                stopped_asset_count,
            ) = self.get_asset_status_counts(assets)

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
                last_tracking_event = await session.execute(
                    session.query(
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
                last_tracking_event = last_tracking_event.first()

                if last_tracking_event:
                    # Construct a dictionary with the retrieved fields
                    last_tracking_event_dict = {
                        "lat": last_tracking_event.lat,
                        "lng": last_tracking_event.lng,
                        "speed": last_tracking_event.speed,
                        "course": last_tracking_event.course,
                        "timestamp": last_tracking_event.timestamp,
                        "event_type": last_tracking_event.event_type,
                        "status": get_status(last_tracking_event.event_type),
                        "fuel_level": last_tracking_event.fuel_level,
                    }
                    # Add last_tracking_event_dict to asset dictionary
                    asset.last_tracking_event = last_tracking_event_dict

            # Fetch the assigned operator from AssetOperatorAssignment
            operator_assignment = await session.execute(
                session.query(AssetOperatorAssignment)
                .filter(AssetOperatorAssignment.asset_uuid == asset.uuid)
                .limit(1)
            )
            operator_assignment = operator_assignment.first()

            if operator_assignment:
                # Fetch the operator (user) details
                operator = await session.execute(
                    session.query(User)
                    .filter(User.uuid == operator_assignment.operator_uuid)
                    .limit(1)
                )
                operator = operator.first()

                if operator:
                    operator_data = {
                        "uuid": operator.uuid,
                        "first_name": operator.first_name,
                        "last_name": operator.last_name,
                        "email": operator.email_address,
                        "image_url": operator.avatar_url,
                        "operator_type": operator.operator_type,
                        "phone_number": operator.phone_number,
                    }
                    # Add operator_data to asset dictionary
                    asset.operator = operator_data
                else:
                    asset.operator = None
            else:
                asset.operator = None

        return assets

    async def read_all_third_party_assets(
        self, asset_type_uuid: str = None, page=1, page_size=10
    ):
        async with self.session_factory() as session:
            # Calculate the offset based on the page and per_page values
            offset = (page - 1) * page_size

            query = session.query(self.model).filter(
                self.model.created_by == AssetCreators.DVLA
            )
            total_assets = await session.execute(query.count())
            total_assets = total_assets.scalar()

            if asset_type_uuid is not None:
                query = query.filter(self.model.asset_type_uuid == asset_type_uuid)

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = await session.execute(
                query.options(joinedload(Asset.asset_type))
                .options(joinedload(Asset.driver))
                .options(joinedload(Asset.device))
                .options(joinedload(Asset.equipment))
                .options(joinedload(Asset.vehicle_owner))
            )
            assets = assets.unique().scalars().all()

            return assets, total_assets

    async def read_all_stolen_assets(
        self, asset_type_uuid: str = None, page=1, page_size=10
    ):
        async with self.session_factory() as session:
            # Calculate the offset based on the page and per_page values
            offset = (page - 1) * page_size

            query = session.query(self.model).filter(
                self.model.asset_stolen_status.is_(True)
            )
            total_assets = await session.execute(query.count())
            total_assets = total_assets.scalar()

            if asset_type_uuid is not None:
                query = query.filter(self.model.asset_type_uuid == asset_type_uuid)

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = await session.execute(
                query.options(joinedload(Asset.asset_type))
                .options(joinedload(Asset.driver))
                .options(joinedload(Asset.device))
                .options(joinedload(Asset.equipment))
                .options(joinedload(Asset.vehicle_owner))
            )
            assets = assets.unique().scalars().all()

            for asset in assets:
                # check if asset has device imei
                if asset.device_imei:
                    # Get device's last known location
                    last_tracking_event = await session.execute(
                        session.query(
                            label("lat", TrackingEvent.latitude),
                            label("lng", TrackingEvent.longitude),
                            TrackingEvent.speed,
                            TrackingEvent.course,
                            label("timestamp", TrackingEvent.event_datetime),
                            label("event_type", TrackingEvent.event_type),
                        )
                        .filter(TrackingEvent.device_imei == asset.device_imei)
                        .order_by(desc(TrackingEvent.event_datetime))
                        .limit(1)
                    )
                    last_tracking_event = last_tracking_event.first()

                    if last_tracking_event:
                        # Construct a dictionary with the retrieved fields
                        last_tracking_event_dict = {
                            "lat": last_tracking_event.lat,
                            "lng": last_tracking_event.lng,
                            "speed": last_tracking_event.speed,
                            "course": last_tracking_event.course,
                            "timestamp": last_tracking_event.timestamp,
                            "event_type": last_tracking_event.event_type,
                        }
                        # Add last_tracking_event_dict to asset dictionary
                        asset.last_tracking_event = last_tracking_event_dict

            return assets, total_assets

    async def assign_device_imei(
        self, asset_uuid, payload: AssignDeviceInputPayload
    ) -> Asset:
        async with self.session_factory() as session:
            device = await session.execute(
                session.query(Device).filter(Device.device_imei == payload.device_imei)
            )
            device = device.scalar()

            # check if imei is valid
            if not device:
                raise Exception(f"Device with imei {payload.device_imei} not found")

            # check if device already assigned
            if device.assign_to_asset_status is not None:
                raise Exception("Device already assigned to an asset")

            asset = await session.execute(
                session.query(self.model).filter(self.model.uuid == asset_uuid)
            )
            asset = asset.scalar()

            # check if asset exist
            if not asset:
                raise Exception(f"Asset with id {asset_uuid} not found")

            # update asset with device imei
            asset.device_imei = payload.device_imei
            asset.asset_status = AssetStatus.ACTIVE
            await session.commit()
            await session.refresh(asset)

            # update device with user_uuid, business_uuid if user type is business
            user = await session.execute(
                session.query(User).filter(User.uuid == asset.user_uuid)
            )
            user = user.scalar()

            device.assign_to_asset_status = datetime.now()
            device.user_uuid = user.uuid
            device.sim_phone_number = payload.sim_phone_number

            if user.business_profile_uuid:
                device.business_profile_uuid = user.business_profile_uuid

            await session.commit()
            await session.refresh(device)

            updated_asset = await session.execute(
                session.query(self.model).filter(self.model.uuid == asset_uuid)
            )
            updated_asset = updated_asset.scalar()

            return updated_asset

    async def read_by_vin_serial_number_license_no(
        self, vin: str = None, serial_number: str = None, vehicle_license_no: str = None
    ):
        async with self.session_factory() as session:
            if vehicle_license_no:
                existing_asset = await session.execute(
                    session.query(self.model).filter(
                        self.model.vehicle_license_no == vehicle_license_no
                    )
                )
                existing_asset = existing_asset.scalar()
                if existing_asset:
                    raise Exception(
                        "Asset with the given license number already exists."
                    )
            if vin:
                existing_asset = await session.execute(
                    session.query(self.model).filter(self.model.vin == vin)
                )
                existing_asset = existing_asset.scalar()
                if existing_asset:
                    raise Exception("Asset with the given VIN already exists.")
            if serial_number:
                existing_asset = await session.execute(
                    session.query(self.model).filter(
                        self.model.serial_number == serial_number
                    )
                )
                existing_asset = existing_asset.scalar()
                if existing_asset:
                    raise Exception(
                        "Asset with the given serial number already exists."
                    )
            else:
                pass

    async def update_asset_stolen_status_to_true(self, asset_uuid: str):
        async with self.session_factory() as session:
            asset = await session.execute(
                session.query(self.model).filter(self.model.uuid == asset_uuid)
            )
            asset = asset.scalar()
            asset.asset_stolen_status = True
            await session.commit()
            await session.refresh(asset)

    async def update_asset_stolen_status_to_false(self, asset_uuid: str):
        async with self.session_factory() as session:
            asset = await session.execute(
                session.query(self.model).filter(self.model.uuid == asset_uuid)
            )
            asset = asset.scalar()
            asset.asset_stolen_status = False
            await session.commit()
            await session.refresh(asset)

    async def get_over_speeding_violations(
        self,
        asset_uuid: str,
        alert_policy_type_uuid: str,  # This might be an enum, ensure it's converted
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
        async with self.session_factory() as session:  # type: AsyncSession
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
            base_query = (
                session.query(MaintenanceAlert)
                .options(joinedload(MaintenanceAlert.alert_policy))
                .filter(
                    cast(MaintenanceAlert.created_at, Date)
                    >= datetime.strptime(start_date, "%d/%m/%Y"),
                    cast(MaintenanceAlert.created_at, Date)
                    <= datetime.strptime(end_date, "%d/%m/%Y"),
                    MaintenanceAlert.asset_uuid == asset_uuid,
                )
            )

            # Execute the query and fetch results
            maintenance_alerts = await session.execute(base_query)
            return maintenance_alerts.unique().scalars().all()

    async def get_asset_by_user_uuid(self, user_uuid: str):
        async with self.session_factory() as session:
            return await session.execute(
                session.query(self.model).filter(self.model.user_uuid == user_uuid)
            ).scalar()

    async def get_asset_by_license_no(self, vehicle_license_no: str):
        async with self.session_factory() as session:
            asset = await session.execute(
                session.query(self.model).filter(
                    self.model.vehicle_license_no == vehicle_license_no
                )
            ).scalar()
            return asset

    async def get_driver_by_asset_uuid(self, asset_uuid: str):
        async with self.session_factory() as session:
            return await session.execute(
                session.query(Driver)
                .join(Asset, Driver.asset_uuid == Asset.uuid)
                .filter(Asset.uuid == asset_uuid)
            ).scalar()

    async def get_asset_by_driver_email(self, driver_email: str):
        async with self.session_factory() as session:
            return await session.execute(
                session.query(Asset)
                .join(Driver, Asset.uuid == Driver.asset_uuid)
                .filter(Driver.email == driver_email)
            ).scalar()

    async def get_assets_by_imeis(self, imeis: List[str]):
        async with self.session_factory() as session:
            assets = await session.execute(
                session.query(Asset).filter(Asset.device_imei.in_(imeis))
            )
            return assets.scalars().all()

    async def get_all_device_imeis(self):
        """Asynchronously retrieves all distinct device IMEIs from the Asset table."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Asset.device_imei)
                .where(Asset.device_imei.isnot(None))
                .distinct()
            )

            return [imei for (imei) in result.scalars().all()]
