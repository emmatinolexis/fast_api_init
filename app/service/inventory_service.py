from app.repository.device_image_repository import DeviceImageRepository
from app.repository.device_repository import DeviceRepository
from app.repository.inventory_repository import InventoryRepository
from app.schema.device_schema import InventoryPayload
from app.service.base_service import BaseService


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

    def create_inventory(self, device_payload: InventoryPayload):
        try:
            inventory = self.inventory_repository.create_inventory(device_payload)
            self.device_repository.create_devices(inventory)
            for image in device_payload.images:
                self.device_image_repository.create_image(
                    inventory_uuid=inventory.uuid, image=image
                )
            return inventory
        except Exception as e:
            raise e

    def get_all_inventory(self, page=1, page_size=10, search_query=None):
        try:
            inventories = self.inventory_repository.get_all_inventory(
                page=page, 
                page_size=page_size, 
                search_query=search_query  
            )
            return inventories
        except Exception as e:
            raise e
    
   
        


