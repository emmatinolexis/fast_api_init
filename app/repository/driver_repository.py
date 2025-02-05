from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Dict

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.driver import Driver
from app.repository.base_repository import BaseRepository


class DriverRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Driver)

    async def get_drivers_by_user_uuid(
        self, user_uuid: str, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of drivers
            count_query = (
                select(func.count(self.model.id))
                .filter(self.model.user_uuid == user_uuid)
            )
            total_result = await session.execute(count_query)
            total_drivers = total_result.scalar()

            # Calculate total pages
            total_pages = (total_drivers + page_size - 1) // page_size

            # Query to get the paginated drivers
            drivers_query = (
                select(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )
            result = await session.execute(drivers_query)
            drivers = result.scalars().all()

            return {
                "drivers": drivers,
                "total_drivers": total_drivers,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def update_driver_asset(self, asset_uuid: str, driver_uuid: str) -> Driver:
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.uuid == driver_uuid)
                result = await session.execute(query)
                driver = result.scalar_one_or_none()

                if driver:
                    driver.asset_uuid = asset_uuid
                    await session.commit()
                    await session.refresh(driver)
                    return driver
                raise Exception("Driver not found")
            except Exception as e:
                await session.rollback()
                raise e

    async def get_drivers_by_business_uuid(
        self, business_uuid: str, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of drivers
            count_query = (
                select(func.count(self.model.id))
                .filter(self.model.business_uuid == business_uuid)
            )
            total_result = await session.execute(count_query)
            total_drivers = total_result.scalar()

            # Calculate total pages
            total_pages = (total_drivers + page_size - 1) // page_size

            # Fetch paginated results
            drivers_query = (
                select(self.model)
                .filter(self.model.business_uuid == business_uuid)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )
            result = await session.execute(drivers_query)
            drivers = result.scalars().all()

            return {
                "drivers": drivers,
                "total_drivers": total_drivers,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_driver_phone_number(self, phone_number: str) -> Driver:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .filter(self.model.phone_number == phone_number)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def unassign_driver(self, driver_uuid: str) -> Driver:
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.uuid == driver_uuid)
                result = await session.execute(query)
                driver = result.scalar_one_or_none()
                
                if not driver:
                    raise Exception("Driver not found")
                
                driver.asset_uuid = None
                await session.commit()
                await session.refresh(driver)
                return driver
            except Exception as e:
                await session.rollback()
                raise e

    async def get_driver_by_email(self, email: str) -> Driver:
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_driver_by_asset_uuid(self, asset_uuid: str) -> Driver:
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.asset_uuid == asset_uuid)
            result = await session.execute(query)
            return result.scalar_one_or_none()