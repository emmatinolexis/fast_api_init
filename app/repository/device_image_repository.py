from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from app.model.inventory import DeviceImage
from app.repository.base_repository import BaseRepository


class DeviceImageRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DeviceImage)

    def create_image(self, inventory_uuid: str, image: str):
        with self.session_factory() as session:
            try:
                image_data = DeviceImage(inventory_uuid=inventory_uuid, image_url=image)
                session.add(image_data)
                session.commit()
                session.refresh(image_data)
            except Exception as e:
                session.rollback()
                raise e

    def update_images(self, inventory_uuid: UUID, new_image: str):
        with self.session_factory() as session:
            try:
                session.query(DeviceImage).filter(
                    DeviceImage.inventory_uuid == inventory_uuid
                ).delete()

                image_record = DeviceImage(
                    inventory_uuid=inventory_uuid, image_url=new_image
                )
                session.add(image_record)

                session.commit()
            except Exception as e:
                session.rollback()
                raise e
