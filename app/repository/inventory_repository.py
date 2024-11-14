import uuid
from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy import or_
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

    def get_all_inventory(self, page=1, page_size=10, search_query=None):
        with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                base_query = session.query(self.model).options(
                    joinedload(Inventory.manufacturer), joinedload(Inventory.images)
                )

                if search_query:
                    device_name_filter = Inventory.device_name.ilike(
                        f"%{search_query}%"
                    )

                    base_query = base_query.filter(
                        or_(
                            device_name_filter,
                        )
                    )

                total_inventories = base_query.count()
                paginated_query = base_query.offset(offset).limit(page_size)
                inventories = paginated_query.all()

                total_in_stock = (
                    session.query(self.model).filter(self.model.quantity > 0).count()
                )
                total_out_of_stock = (
                    session.query(self.model).filter(self.model.quantity == 0).count()
                )

                return {
                    "inventories": inventories,
                    "total_inventories": total_inventories,
                    "total_pages": (total_inventories + page_size - 1) // page_size,
                    "current_page": page,
                    "page_size": page_size,
                    "total_in_stock": total_in_stock,
                    "total_out_of_stock": total_out_of_stock,
                }
            except Exception as e:
                session.rollback()
                raise e

    def reduce_inventory_no(self, inventory_uuid: uuid, quantity: int):
        with self.session_factory() as session:
            try:
                inventory = (
                    session.query(self.model)
                    .filter(self.model.uuid == inventory_uuid)
                    .first()
                )
                inventory.quantity = inventory.quantity - quantity
                session.commit()
                session.refresh(inventory)
                return inventory
            except Exception as e:
                session.rollback()
                raise e

    def get_inventory_by_uuid(self, inventory_uuid: UUID):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(Inventory.manufacturer), joinedload(Inventory.images))
                .filter(self.model.uuid == inventory_uuid)
                .first()
            )

    def save_inventory(self, inventory):
        with self.session_factory() as session:
            try:
                session.add(inventory)
                session.commit()
                session.refresh(inventory)
                return inventory
            except Exception as e:
                session.rollback()
                raise e
