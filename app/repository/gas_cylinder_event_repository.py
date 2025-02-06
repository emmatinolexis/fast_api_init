from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import Date, and_, cast
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.gas_cylinders import GasCylinderEvent
from app.repository.base_repository import BaseRepository


class GasCylinderEventRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, GasCylinderEvent)

    async def read_all_gas_events_by_date_range(
        self, device_serial_number: str, start_date: str, end_date: str
    ):
        async with self.session_factory() as session:
            # Convert string dates to datetime objects before querying
            start_dt = datetime.strptime(start_date, "%d/%m/%Y")
            end_dt = datetime.strptime(end_date, "%d/%m/%Y")
            stmt = (
                select(self.model)
                .filter(
                    self.model.device_serial_number == device_serial_number,
                    and_(
                        cast(self.model.event_timestamp, Date) >= start_dt,
                        cast(self.model.event_timestamp, Date) <= end_dt,
                    ),
                )
                .order_by(self.model.event_timestamp)
            )

            result = await session.execute(stmt)
            return result.scalars().all()
