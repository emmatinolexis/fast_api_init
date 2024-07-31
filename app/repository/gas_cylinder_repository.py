from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.gas_cylinders import GasCylinder
from app.repository.base_repository import BaseRepository
from app.schema.gas_cylinder_schema import CreateGasCylinderPayload
from app.util.enums import ActiveStatus


class GasCylinderRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, GasCylinder)

    def read_all_cylinders_no_pagination(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        cylinder_uuid: str = None,
    ):
        with self.session_factory() as session:
            if user_uuid is not None:
                if cylinder_uuid:
                    return (
                        session.query(self.model)
                        .filter(self.model.uuid == cylinder_uuid)
                        .all()
                    )
                else:
                    return (
                        session.query(self.model)
                        .filter(self.model.user_uuid == user_uuid)
                        .all()
                    )

            if business_uuid is not None:
                if cylinder_uuid:
                    return (
                        session.query(self.model)
                        .filter(self.model.uuid == cylinder_uuid)
                        .all()
                    )
                else:
                    return (
                        session.query(self.model)
                        .filter(self.model.business_profile_uuid == business_uuid)
                        .all()
                    )

            return []

    def get_gas_cylinder_by_building_uuid(
        self, building_uuid: str, cylinder_status: str = None
    ):
        with self.session_factory() as session:
            query = session.query(self.model).filter(
                self.model.building_uuid == building_uuid
            )
            if cylinder_status:
                query = query.filter(self.model.status == cylinder_status)
            return query.all()

    def create_gas_cylinder(
        self,
        gas_payload: CreateGasCylinderPayload,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        with self.session_factory() as session:
            existing_gas = self._find_existing_gas(
                session, gas_payload.gas_device_serial_number
            )

            if existing_gas:
                self._deactivate_existing_gas(existing_gas)

                if gas_payload.gas_cylinder_uuid:
                    return self._link_existing_gas_cylinder(session, gas_payload)
                else:
                    return self._create_new_gas_cylinder(
                        session, gas_payload, user_uuid, business_uuid
                    )
            else:
                return self._create_new_gas_cylinder(
                    session, gas_payload, user_uuid, business_uuid
                )

    def _find_existing_gas(self, session, gas_device_serial_number):
        return (
            session.query(self.model)
            .filter(self.model.gas_device_serial_number == gas_device_serial_number)
            .first()
        )

    def _deactivate_existing_gas(self, existing_gas):
        existing_gas.gas_device_serial_number = None
        existing_gas.status = ActiveStatus.INACTIVE

    def _link_existing_gas_cylinder(self, session, gas_payload):
        gas_to_link = (
            session.query(self.model)
            .filter(self.model.uuid == gas_payload.gas_cylinder_uuid)
            .first()
        )

        if gas_to_link:
            gas_to_link.gas_device_serial_number = gas_payload.gas_device_serial_number
            gas_to_link.status = ActiveStatus.ACTIVE
            session.commit()
            session.refresh(gas_to_link)
            return gas_to_link

        raise ValueError(
            f"Gas cylinder with UUID {gas_payload.gas_cylinder_uuid} not found"
        )

    def _create_new_gas_cylinder(self, session, gas_payload, user_uuid, business_uuid):
        gas_data = GasCylinder(
            cylinder_name=gas_payload.cylinder_name,
            material_type=gas_payload.material_type,
            gas_device_serial_number=gas_payload.gas_device_serial_number,
            cylinder_type_uuid=gas_payload.cylinder_type_uuid,
            building_uuid=gas_payload.building_uuid,
            user_uuid=user_uuid,
            business_profile_uuid=business_uuid,
        )
        session.add(gas_data)
        session.commit()
        session.refresh(gas_data)
        return gas_data
