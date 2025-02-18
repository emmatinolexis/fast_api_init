from typing import Callable, Optional

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.device import Device, DeviceManufacturer
from app.model.inventory import Inventory
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import AccountType, DeviceStatus


class DeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Device)

    async def get_all_devices(
        self,
        page: int = 1,
        page_size: int = 10,
        search_query: Optional[str] = None,
        status=None,
    ):
        async with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                # Base query with joins
                base_query = select(self.model).options(
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
                                DeviceManufacturer.manufacturer_name.ilike(
                                    f"%{search_query}%"
                                ),
                                Device.device_imei.ilike(f"%{search_query}%"),
                            )
                        )
                    )

                # Apply status filter
                if status == DeviceStatus.ASSIGNED:
                    base_query = base_query.filter(
                        self.model.assign_to_asset_status.isnot(None)
                    )
                elif status == DeviceStatus.NOT_ASSIGNED:
                    base_query = base_query.filter(
                        self.model.assign_to_asset_status.is_(None)
                    )

                # Order by created_at in descending order
                base_query = base_query.order_by(desc(self.model.created_at))

                # Get total count of devices
                total_result = await session.execute(
                    select(func.count()).select_from(base_query.subquery())
                )
                total_devices = total_result.scalar()

                # Apply pagination
                paginated_query = base_query.offset(offset).limit(page_size)
                result = await session.execute(paginated_query)
                devices = result.unique().scalars().all()

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
                await session.rollback()
                raise e

    async def get_all_devices_to_assign(
        self,
        page: int = 1,
        page_size: int = 10,
        search_query: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                base_query = (
                    select(self.model)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.asset),
                        joinedload(Device.user),
                    )
                    .filter(
                        Device.device_imei.isnot(None),
                        self.model.assign_to_asset_status.is_(None),
                    )
                )

                if search_query:
                    base_query = (
                        base_query.join(Device.inventory)
                        .join(Inventory.manufacturer)
                        .filter(
                            or_(
                                DeviceManufacturer.manufacturer_name.ilike(
                                    f"%{search_query}%"
                                ),
                                Device.device_imei.ilike(f"%{search_query}%"),
                            )
                        )
                    )

                total_result = await session.execute(
                    select(func.count()).select_from(base_query.subquery())
                )
                total_devices = total_result.scalar()

                paginated_query = base_query.offset(offset).limit(page_size)
                result = await session.execute(paginated_query)
                devices = result.unique().scalars().all()

                total_pages = (total_devices + page_size - 1) // page_size

                return {
                    "devices": devices,
                    "total_devices": total_devices,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                }
            except Exception as e:
                await session.rollback()
                raise e

    async def get_user_data_by_device_uuid(self, device_imei: str):
        async with self.session_factory() as session:
            try:
                query = (
                    select(self.model)
                    .filter(self.model.device_imei == device_imei)
                    .options(
                        joinedload(Device.inventory).joinedload(Inventory.manufacturer),
                        joinedload(Device.user),
                    )
                )
                result = await session.execute(query)
                device = result.unique().scalar_one_or_none()

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

    async def create_devices(self, inventory):
        async with self.session_factory() as session:
            try:
                devices = [
                    Device(device_inventory_uuid=inventory.uuid)
                    for _ in range(inventory.quantity)
                ]
                session.add_all(devices)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def get_devices_by_user_uuid(self, user_uuid):
        async with self.session_factory() as session:
            user_query = select(User).filter(User.uuid == user_uuid)
            result = await session.execute(user_query)
            user = result.scalar_.one_or_none()

            if not user:
                raise Exception("User not found")

            if user.account_type == AccountType.INDIVIDUAL:
                query = (
                    select(self.model)
                    .filter(self.model.user_uuid == user.uuid)
                    .options(
                        joinedload(Device.asset),
                        joinedload(Device.inventory).joinedload(Inventory.images),
                    )
                )
            else:  # AccountType.BUSINESS
                query = (
                    select(self.model)
                    .filter(
                        self.model.business_profile_uuid == user.business_profile_uuid
                    )
                    .options(
                        joinedload(Device.asset),
                        joinedload(Device.inventory).joinedload(Inventory.images),
                    )
                )

            result = await session.execute(query)
            return result.unique().scalars().all()

    async def get_devices_by_business_uuid(self, business_uuid):
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .options(
                    joinedload(Device.asset),
                    joinedload(Device.inventory).joinedload(Inventory.images),
                )
            )
            result = await session.execute(query)
            return result.unique().scalars().all()

    async def assign_imei(self, device_uuid, imei):
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.uuid == device_uuid)
                result = await session.execute(query)
                device = result.scalar_.one_or_none()

                if not device:
                    raise Exception(f"Device not found for the ID: {device_uuid}")

                device.device_imei = imei
                await session.commit()
                await session.refresh(device)
                return device
            except Exception as e:
                await session.rollback()
                raise e

    async def get_device_for_engine_shutdown(self, device_imei: str):
        async with self.session_factory() as session:
            try:
                query = (
                    select(self.model)
                    .filter(self.model.device_imei == device_imei)
                    .options(
                        joinedload(Device.asset),
                        joinedload(Device.manufacturer),
                    )
                )
                result = await session.execute(query)
                return result.unique().scalar_.one_or_none()
            except Exception as e:
                raise e
