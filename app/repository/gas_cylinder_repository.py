from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext import AsynSession, joinedload
from sqlalchemy.future import select

from app.model.gas_cylinders import GasCylinder
from app.repository.base_repository import BaseRepository
from app.schema.gas_cylinder_schema import CreateGasCylinderPayload
from app.util.enums import ActiveStatus
from app.util.utils import calculate_gas_level_percentage


class GasCylinderRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, GasCylinder)

    async def read_all_cylinders_no_pagination(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        cylinder_uuid: str = None,
    ):
        async with self.session_factory() as session:
            stmt = select(self.model)  # Start with base query

            # Filter by `cylinder_uuid` if provided (highest priority)
            if cylinder_uuid:
                stmt = stmt.filter(self.model.uuid == cylinder_uuid)

            # If no cylinder_uuid, filter by `user_uuid` or `business_uuid`
            elif user_uuid:
                stmt = stmt.filter(self.model.user_uuid == user_uuid)
            elif business_uuid:
                stmt = stmt.filter(self.model.business_profile_uuid == business_uuid)

            # Execute query
            result = await session.execute(stmt)
            cylinders = result.scalars().all()

            return cylinders

    async def get_gas_cylinder_by_building_uuid(
        self, building_uuid: str, cylinder_status: str = None
    ):
        async with self.session_factory() as session:
            stmt = select(self.model).filter(self.model.building_uuid == building_uuid)

            # Apply status filter before execution
            if cylinder_status:
                stmt = stmt.filter(self.model.status == cylinder_status)

            result = await session.execute(stmt)
            cylinders = result.scalars().all()

            return cylinders

    async def read_all_by_user_uuid(self, user_uuid: str):
        with self.session_factory() as session:
            query = await session.execute(
                select(self.model).filter(self.model.user_uuid == user_uuid)
            )
            result = await session.execute(stmt)
            result = query.scalars().all()
            return result

    async def create_gas_cylinder(
        self,
        gas_payload: CreateGasCylinderPayload,
        user_uuid: str = None,
        business_uuid: str = None,
    ):
        async with self.session_factory() as session:
            if gas_payload.gas_cylinder_uuid:
                return await self._link_existing_gas_cylinder(session, gas_payload)
            else:
                await self._unlink_existing_gas_cylinder(
                    session, gas_payload
                )  # ✅ Awaited
                return await self._create_new_gas_cylinder(
                    session, gas_payload, user_uuid, business_uuid
                )

    async def _link_existing_gas_cylinder(self, session, gas_payload):
        result = await session.execute(
            select(self.model).filter(self.model.uuid == gas_payload.gas_cylinder_uuid)
        )
        gas_to_link = result.scalars().first()

        if gas_to_link:
            gas_to_link.gas_device_serial_number = gas_payload.gas_device_serial_number
            gas_to_link.status = ActiveStatus.ACTIVE
            await session.commit()
            await session.refresh(gas_to_link)
            return gas_to_link

        raise ValueError(
            f"Gas cylinder with UUID {gas_payload.gas_cylinder_uuid} not found"
        )

    async def _unlink_existing_gas_cylinder(self, session, gas_payload):
        result = await session.execute(
            select(self.model).filter(
                self.model.gas_device_serial_number
                == gas_payload.gas_device_serial_number
            )
        )
        gas_to_unlink = result.scalars().first()
        if gas_to_unlink:
            gas_to_unlink.gas_device_serial_number = None
            gas_to_unlink.status = ActiveStatus.INACTIVE
            await session.commit()
            await session.refresh(gas_to_unlink)
            return gas_to_unlink

        raise ValueError(
            f"Gas cylinder with serial number {gas_payload.gas_device_serial_number} not found"
        )

    async def _find_existing_gas(self, session, cylinder_uuid):
        result = await session.execute(
            select(self.model).filter(self.model.uuid == cylinder_uuid)
        )
        return result.scalars().first()

    def _deactivate_existing_gas(self, existing_gas):
        existing_gas.gas_device_serial_number = None
        existing_gas.status = ActiveStatus.INACTIVE

    async def _create_new_gas_cylinder(
        self, session, gas_payload, user_uuid, business_uuid
    ):
        gas_data = GasCylinder(
            cylinder_name=gas_payload.cylinder_name,
            gas_device_serial_number=gas_payload.gas_device_serial_number,
            cylinder_type_uuid=gas_payload.cylinder_type_uuid,
            building_uuid=gas_payload.building_uuid,
            user_uuid=user_uuid,
            business_profile_uuid=business_uuid,
        )
        session.add(gas_data)
        await session.commit()
        await session.refresh(gas_data)
        return gas_data

    async def read_all_by_business_uuid(self, business_uuid: str):
        async with self.session_factory() as session:
            stmt = select(self.model).filter(
                self.model.business_profile_uuid == business_uuid
            )

            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_gas_cylinder_by_uuid(self, cylinder_uuid: str):
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .options(
                    joinedload(self.model.gas_device),
                    joinedload(self.model.cylinder_type),
                    joinedload(self.model.gas_events),
                )
                .filter(self.model.uuid == cylinder_uuid)
            )

            result = await session.execute(query)
            cylinder = result.scalars().one_or_none()

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

    async def get_cylinder_by_device_serial_number(self, serial_number: str):
        async with self.session_factory() as session:
            stmt = (
                select(self.model)
                .filter(self.model.gas_device_serial_number == serial_number)
                .options(joinedload(self.model.cylinder_type))
            )

            result = await session.execute(stmt)
            return result.scalars().first()
