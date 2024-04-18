from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.inventory import Inventory
from app.repository.base_repository import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Inventory)

    def create_inventory(self, inventory):
        with self.session_factory() as session:
            try:
                inventory_data = Inventory(
                    device_name=inventory.device_name,
                    device_type=inventory.device_type,
                    quantity=inventory.quantity,
                    device_manufacturer_uuid=inventory.device_manufacturer_uuid,
                    cost_price=inventory.cost_price,
                    description=inventory.description,
                    publish_on_site_status=inventory.publish_on_site_status,
                )
                session.add(inventory_data)
                session.commit()
                session.refresh(inventory_data)
                return inventory_data
            except Exception as e:
                session.rollback()
                raise e

    def get_all_inventory(self):
        with self.session_factory() as session:
            try:
                inventories = (
                    session.query(self.model)
                    .options(joinedload(Inventory.manufacturer))
                    .options(
                        joinedload(Inventory.images)
                    )  # Eagerly load manufacturer relationship
                    .all()
                )
                return inventories
            except Exception as e:
                session.rollback()
                raise e
