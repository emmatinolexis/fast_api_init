from contextlib import AbstractAsyncContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.model.inventory import DeviceImage
from app.repository.base_repository import BaseRepository


class DeviceImageRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceImage)

    async def create_image(self, inventory_uuid: str, image: str):
        async with self.session_factory() as session:
            try:
                image_data = DeviceImage(inventory_uuid=inventory_uuid, image_url=image)
                session.add(image_data)
                await session.commit()
                await session.refresh(image_data)
                return image_data
            except Exception as e:
                await session.rollback()
                raise e

    async def update_images(self, inventory_uuid: UUID, new_image: str):
        async with self.session_factory() as session:
            try:
                # Delete existing images
                stmt = select(DeviceImage).filter(DeviceImage.inventory_uuid == inventory_uuid)
                result = await session.execute(stmt)
                existing_images = result.scalars().all()
                
                for image in existing_images:
                    await session.delete(image)

                # Add new image
                image_record = DeviceImage(inventory_uuid=inventory_uuid, image_url=new_image)
                session.add(image_record)

                await session.commit()
                return image_record
            except Exception as e:
                await session.rollback()
                raise e
