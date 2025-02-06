from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy import String, asc, cast, desc, nulls_last
from sqlalchemy.ext import AsynSession, joinedload

from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository
from app.util.enums import PeripheralDeviceType


class PeripheralDeviceRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, PeripheralDevice)

    def read_all(self, page=1, page_size=10, device_type=None, search=None):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            base_query = session.query(self.model)

            if device_type:
                base_query = base_query.filter(
                    self.model.device_type == device_type.value
                )

            if search:
                search_pattern = f"%{search}%"
                base_query = base_query.filter(
                    (self.model.serial_number.ilike(search_pattern))
                    | (cast(self.model.device_type, String).ilike(search_pattern))
                )

            total_devices = base_query.count()
            total_pages = (total_devices + page_size - 1) // page_size

            paginated_query = (
                base_query.order_by(asc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )
            devices = paginated_query.all()

        return {
            "devices": devices,
            "total_devices": total_devices,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
        }

    def get_last_device(self, device_type: PeripheralDeviceType):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.device_type == device_type)
                .order_by(self.model.id.desc())
                .first()
            )

    def get_by_serial_number(self, serial_number: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.serial_number == serial_number)
                .first()
            )

    def get_by_peripheral_device_uuid(self, peripheral_device_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.uuid == peripheral_device_uuid)
                .first()
            )

    def get_device_node_id(self, node_id: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.node_id == node_id)
                .options(joinedload(self.model.building))
                .first()
            )

    def get_user_devices(self, user_uuid, device_type: str = None):
        with self.session_factory() as session:
            base_query = session.query(self.model).filter(
                self.model.user_uuid == user_uuid
            )
            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type)

            base_query = base_query.order_by(
                nulls_last(desc(self.model.installed_at)), desc(self.model.created_at)
            )
            return base_query.order_by(self.model.created_at).all()

    def get_business_devices(self, business_uuid, device_type: str = None):
        with self.session_factory() as session:
            base_query = session.query(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )
            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type)

            base_query = base_query.order_by(
                nulls_last(desc(self.model.installed_at)), desc(self.model.created_at)
            )
            return base_query.order_by(self.model.created_at).all()

    def get_building_devices(self, building_uuid, device_type: str = None):
        with self.session_factory() as session:
            base_query = session.query(self.model).filter(
                self.model.building_uuid == building_uuid
            )
            if device_type:
                base_query = base_query.filter(self.model.device_type == device_type)

            # Order by installed_at if it exists, otherwise order by created_at
            base_query = base_query.order_by(
                nulls_last(desc(self.model.installed_at)), desc(self.model.created_at)
            )

            return base_query.all()

            # Order by installed_at if it exists, otherwise order by created_at
            base_query = base_query.order_by(
                nulls_last(desc(self.model.installed_at)), desc(self.model.created_at)
            )

            return base_query.all()

    def get_device_by_cylinder_uuid(self, cylinder_uuid):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.gas_cylinder_uuid == cylinder_uuid)
                .first()
            )
