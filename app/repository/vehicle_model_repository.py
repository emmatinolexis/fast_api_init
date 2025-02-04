from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.vehicle_models import VehicleModel
from app.repository.base_repository import BaseRepository


class VehicleModelRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, VehicleModel)

    async def get_vehicle_model_name(self, name: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(name=name))
            model = result.scalars().first()
            return model
