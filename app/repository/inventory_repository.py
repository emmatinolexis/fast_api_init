from contextlib import AbstractAsyncContextManager
from typing import Callable
from uuid import UUID

from sqlalchemy.ext import AsynSession, joinedload

from app.model.inventory import Inventory
from app.repository.base_repository import BaseRepository


class InventoryRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Inventory)

    async def create_inventory(self, inventory):
        async with self.session_factory() as session:
            try:
                inventory_data = self.model(
                    device_name=inventory.device_name,
                    device_type=inventory.device_type,
                    quantity=inventory.quantity,
                    device_manufacturer_uuid=inventory.device_manufacturer_uuid,
                    cost_price=inventory.cost_price,
                    description=inventory.description,
                    publish_on_site_status=inventory.publish_on_site_status,
                )
                session.add(inventory_data)
                await session.commit()
                await session.refresh(inventory_data)
                return inventory_data
            except Exception as e:
                await session.rollback()
                raise e

    async def get_all_inventory(self, page=1, page_size=10, search_query=None):
        async with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                # Base query with joinedload
                base_query = select(self.model).options(
                    joinedload(self.model.manufacturer), joinedload(self.model.images)
                )

                # Apply search filter if present
                if search_query:
                    base_query = base_query.filter(
                        self.model.device_name.ilike(f"%{search_query}%")
                    )

                # Fetch total count
                total_result = await session.execute(select(self.model))
                total_inventories = len(total_result.scalars().all())

                # Paginate results
                paginated_result = await session.execute(
                    base_query.offset(offset).limit(page_size)
                )
                inventories = paginated_result.scalars().all()

                # Count total in-stock and out-of-stock inventories
                in_stock_result = await session.execute(
                    select(self.model).filter(self.model.quantity > 0)
                )
                total_in_stock = len(in_stock_result.scalars().all())

                out_of_stock_result = await session.execute(
                    select(self.model).filter(self.model.quantity == 0)
                )
                total_out_of_stock = len(out_of_stock_result.scalars().all())

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
                await session.rollback()
                raise e

    async def reduce_inventory_no(self, inventory_uuid: UUID, quantity: int):
        async with self.session_factory() as session:
            try:
                inventory_query = await session.execute(
                    select(self.model).filter(self.model.uuid == inventory_uuid)
                )
                inventory = inventory_query.scalars().first()

                if not inventory:
                    raise ValueError("Inventory not found")

                inventory.quantity -= quantity

                await session.commit()
                await session.refresh(inventory)
                return inventory
            except Exception as e:
                await session.rollback()
                raise e

    async def get_inventory_by_uuid(self, inventory_uuid: UUID):
        async with self.session_factory() as session:
            inventory_query = await session.execute(
                select(self.model)
                .options(
                    joinedload(self.model.manufacturer), joinedload(self.model.images)
                )
                .filter(self.model.uuid == inventory_uuid)
            )
            return inventory_query.scalars().first()

    async def save_inventory(self, inventory):
        async with self.session_factory() as session:
            try:
                session.add(inventory)
                await session.commit()
                await session.refresh(inventory)
                return inventory
            except Exception as e:
                await session.rollback()
                raise e
