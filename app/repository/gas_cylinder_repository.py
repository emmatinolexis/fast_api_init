from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.gas_cylinders import GasCylinder
from app.repository.base_repository import BaseRepository
from app.schema.gas_cylinder_schema import CreateGasCylinderPayload
from app.util.enums import ActiveStatus
from app.util.utils import calculate_gas_level_percentage


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

    def read_all_by_user_uuid(self, user_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .all()
            )

    def create_gas_cylinder(
        self,
        gas_payload: CreateGasCylinderPayload,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        with self.session_factory() as session:
            if gas_payload.gas_cylinder_uuid:
                return self._link_existing_gas_cylinder(session, gas_payload)
            else:
                return self._create_new_gas_cylinder(
                    session, gas_payload, user_uuid, business_uuid
                )

    def _find_existing_gas(self, session, cylinder_uuid):
        return (
            session.query(self.model).filter(self.model.uuid == cylinder_uuid).first()
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

    def read_all_by_business_uuid(self, business_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == business_uuid)
                .all()
            )

    def get_gas_cylinder_by_uuid(self, cylinder_uuid: str):
        with self.session_factory() as session:
            cylinder = (
                session.query(self.model)
                .options(
                    joinedload(self.model.gas_device),
                    joinedload(self.model.cylinder_type),
                    joinedload(self.model.gas_events),
                    joinedload(self.model.cylinder_type),
                )
                .filter(self.model.uuid == cylinder_uuid)
                .one_or_none()
            )

            gas_level = 0

            if cylinder.gas_device:
                latest_event = max(cylinder.gas_events, key=lambda x: x.created_at)

                gas_level = calculate_gas_level_percentage(
                    cylinder.cylinder_type.empty_weight,
                    cylinder.cylinder_type.full_weight,
                    latest_event.current_weight,
                )

            cylinder = {
                "cylinder_name": cylinder.cylinder_name,
                "material_type": cylinder.material_type,
                "gas_device": {
                    "device_name": cylinder.gas_device.device_name,
                    "device_serial_number": cylinder.gas_device.serial_number,
                },
                "cylinder_type": {
                    "name": cylinder.cylinder_type.name,
                    "full_weight": cylinder.cylinder_type.full_weight,
                    "empty_weight": cylinder.cylinder_type.empty_weight,
                },
                "current_weight": gas_level,
            }

            return cylinder

    def get_cylinder_by_device_serial_number(self, serial_number: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.gas_device_serial_number == serial_number)
                .first()
            )
