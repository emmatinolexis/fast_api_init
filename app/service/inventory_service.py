from uuid import UUID

from app.core.exceptions import NotFoundError
from app.repository.device_image_repository import DeviceImageRepository
from app.repository.device_repository import DeviceRepository
from app.repository.inventory_repository import InventoryRepository
from app.schema.device_schema import InventoryPayload, InventoryUpdatePayload
from app.service.base_service import BaseService
from app.util.utils import send_client_side_error


class InventoryService(BaseService):
    def __init__(
        self,
        inventory_repository: InventoryRepository,
        device_repository: DeviceRepository,
        device_image_repository: DeviceImageRepository,
    ):
        self.inventory_repository = inventory_repository
        self.device_repository = device_repository
        self.device_image_repository = device_image_repository
        super().__init__(inventory_repository)

    async def get_inventory_by_uuid(self, inventory_uuid: UUID):
        try:
            inventory = await self.inventory_repository.get_inventory_by_uuid(
                inventory_uuid
            )
            if not inventory:
                raise NotFoundError(detail=inventory)
            return inventory
        except Exception as e:
            raise e

    async def create_inventory(self, device_payload: InventoryPayload):
        try:
            inventory = await self.inventory_repository.create_inventory(device_payload)
            await self.device_repository.create_devices(inventory)
            for image in device_payload.images:
                await self.device_image_repository.create_image(
                    inventory_uuid=inventory.uuid, image=image
                )
            return inventory
        except Exception as e:
            raise e

    async def get_all_inventory(self, page=1, page_size=10, search_query=None):
        try:
            inventories = await self.inventory_repository.get_all_inventory(
                page=page, page_size=page_size, search_query=search_query
            )
            return inventories
        except Exception as e:
            raise e

    async def update_inventory(
        self, inventory_uuid: UUID, payload: InventoryUpdatePayload
    ):
        try:
            inventory = await self.inventory_repository.get_inventory_by_uuid(
                inventory_uuid
            )
            if not inventory:
                raise NotFoundError(f"Inventory with UUID {inventory_uuid} not found.")

            if payload.device_name:
                inventory.device_name = payload.device_name
            if payload.quantity is not None:
                inventory.quantity = payload.quantity
            if payload.device_manufacturer_uuid:
                inventory.device_manufacturer_uuid = payload.device_manufacturer_uuid
            if payload.cost_price is not None:
                inventory.cost_price = payload.cost_price
            if payload.selling_price is not None:
                inventory.selling_price = payload.selling_price
            if payload.description:
                inventory.description = payload.description
            if payload.image:
                await self.device_image_repository.update_images(
                    inventory_uuid=inventory.uuid, new_image=payload.image
                )

            await self.inventory_repository.save_inventory(inventory)
            return inventory
        except Exception as e:
            raise e
