from contextlib import AbstractContextManager
from typing import Callable, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc
from app.model.device import Device, DeviceManufacturer
from app.model.inventory import Inventory
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import AccountType, DeviceStatus


class DeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Device)

    def get_all_devices(
            self,
            page: int = 1,
            page_size: int = 10,
            search_query: Optional[str] = None,
            status=None,
    ):
        with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                # Base query with joins
                base_query = session.query(self.model).options(
                    joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                    joinedload(Device.asset),
                    joinedload(Device.user),
                )

                # Apply search query filter
                if search_query:
                    base_query = (
                        base_query.join(Device.inventory)
                        .join(Inventory.manufacturer)
                        .filter(
                            or_(
                                Inventory.device_name.ilike(f"%{search_query}%"),
                                DeviceManufacturer.manufacturer_name.ilike(f"%{search_query}%"),
                                Device.device_imei.ilike(f"%{search_query}%"),
                            )
                        )
                    )

                # Apply status filter
                if status == DeviceStatus.ASSIGNED:
                    base_query = base_query.filter(self.model.assign_to_asset_status.isnot(None))
                elif status == DeviceStatus.NOT_ASSIGNED:
                    base_query = base_query.filter(self.model.assign_to_asset_status.is_(None))

                # Order by created_at in descending order
                base_query = base_query.order_by(desc(self.model.created_at))

                # Get total count of devices
                total_devices = base_query.count()

                # Apply pagination
                paginated_query = base_query.offset(offset).limit(page_size)
                devices = paginated_query.all()

                # Calculate total pages
                total_pages = (total_devices + page_size - 1) // page_size

                return {
                    "devices": devices,
                    "total_devices": total_devices,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                }
            except Exception as e:
                session.rollback()
                raise e

    def get_all_devices_to_assign(
            self,
            page: int = 1,
            page_size: int = 10,
            search_query: Optional[str] = None,
    ):
        with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                # Base query with filters for device_imei and assign_to_asset_status
                base_query = (
                    session.query(self.model)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.asset),
                        joinedload(Device.user),
                    )
                    .filter(
                        Device.device_imei.isnot(None),  # Filter where device_imei is not null
                        self.model.assign_to_asset_status.is_(None),  # Filter where asset_assign_status is null
                    )
                )

                # Apply search query filter
                if search_query:
                    base_query = (
                        base_query.join(Device.inventory)
                        .join(Inventory.manufacturer)
                        .filter(
                            or_(
                                DeviceManufacturer.manufacturer_name.ilike(f"%{search_query}%"),
                                Device.device_imei.ilike(f"%{search_query}%"),  # IMEI included in search
                            )
                        )
                    )

                # Get total count of devices
                total_devices = base_query.count()

                # Apply pagination
                paginated_query = base_query.offset(offset).limit(page_size)
                devices = paginated_query.all()

                # Calculate total pages
                total_pages = (total_devices + page_size - 1) // page_size

                return {
                    "devices": devices,
                    "total_devices": total_devices,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                }
            except Exception as e:
                session.rollback()
                raise e

    def get_user_data_by_device_uuid(self, device_imei: str):
        with self.session_factory() as session:
            try:
                device = (
                    session.query(self.model)
                    .filter(self.model.device_imei == device_imei)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.user),
                    )
                    .first()
                )
                if device:
                    if device.user_uuid:
                        if device.user:
                            del device.user.__dict__["password"]
                        return device
                    else:
                        raise Exception("There is no user assigned to this device")
                else:
                    raise Exception(
                        f"There is no device with the given imei: {device_imei}"
                    )
            except Exception as e:
                raise e

    def create_devices(self, inventory):
        with self.session_factory() as session:
            devices = []
            for _ in range(inventory.quantity):
                device = Device(device_inventory_uuid=inventory.uuid)
                devices.append(device)
            session.add_all(devices)
            session.commit()

    def get_devices_by_user_uuid(self, user_uuid):
        with self.session_factory() as session:
            user = session.query(User).filter(User.uuid == user_uuid).first()

            if not user:
                raise Exception("User not found")

            if user.account_type == AccountType.INDIVIDUAL:
                devices = (
                    session.query(self.model)
                    .filter(self.model.user_uuid == user.uuid)
                    .options(joinedload(Device.asset))
                    .options(joinedload(Device.inventory).joinedload(Inventory.images))
                    .all()
                )

            if user.account_type == AccountType.BUSINESS:
                devices = (
                    session.query(self.model)
                    .filter(
                        self.model.business_profile_uuid == user.business_profile_uuid
                    )
                    .options(joinedload(Device.asset))
                    .options(joinedload(Device.inventory).joinedload(Inventory.images))
                    .all()
                )

            return devices

    def get_devices_by_business_uuid(self, business_uuid):
        with self.session_factory() as session:
            devices = (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .options(joinedload(Device.asset))
                .options(joinedload(Device.inventory).joinedload(Inventory.images))
                .all()
            )
            return devices

    def assign_imei(self, device_uuid, imei):
        with self.session_factory() as session:
            try:
                device = (
                    session.query(self.model)
                    .filter(self.model.uuid == device_uuid)
                    .first()
                )
                if not device:
                    raise Exception(f"Device not found for the ID: {device_uuid}")
                device.device_imei = imei
                session.commit()
                session.refresh(device)
                return device
            except Exception as e:
                session.rollback()
                raise e

    def get_device_for_engine_shutdown(self, device_imei: str):
        with self.session_factory() as session:
            try:
                device = (
                    session.query(self.model)
                    .filter(self.model.device_imei == device_imei)
                    .options(
                        joinedload(Device.asset),
                    )
                    .options(
                        joinedload(Device.manufacturer),
                    )
                    .first()
                )
                return device
            except Exception as e:
                raise e
