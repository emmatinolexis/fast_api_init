import uuid
from datetime import datetime
from typing import Callable, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import cast

from app.model.vehicle_models import AssetType, VehicleMake
from app.repository.base_repository import BaseRepository
from app.schema.asset_schema import VehicleMakeInput
from sqlalchemy.dialects.postgresql import ENUM


class VehicleMakeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, VehicleMake)

    async def create(self, make_input: VehicleMakeInput) -> VehicleMake:
        async with self.session_factory() as session:
            new_make = self.model(
                uuid=uuid.uuid4(),
                name=make_input.name,
                asset_type=make_input.asset_type.upper(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

        session.add(new_make)
        await session.commit()
        await session.refresh(new_make)
        return new_make

    async def get_vehicle_makes(self, asset_type=None) -> List[VehicleMake]:
        async with self.session_factory() as session:
            query = select(self.model)
            if asset_type:
                query = query.filter(self.model.asset_type == asset_type.upper())
            result = await session.execute(query)
            makes = result.scalars().all()
            return makes

    async def get_vehicle_make_by_uuid(self, make_uuid) -> Optional[VehicleMake]:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .options(joinedload(self.model.models))
                .filter_by(uuid=make_uuid)
            )
            result = await session.execute(query)
            make = result.unique().scalars().first()
            return make

    async def get_vehicle_make_name(self, name: str) -> Optional[VehicleMake]:
        async with self.session_factory() as session:
            query = select(self.model).filter_by(name=name)
            result = await session.execute(query)
            make = result.scalars().first()
            return make
