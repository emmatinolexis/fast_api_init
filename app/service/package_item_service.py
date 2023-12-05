from app.repository.package_item_repository import PackageItemRepository
from app.service.base_service import BaseService


class PackageItemService(BaseService):
    def __init__(self, package_item_repository: PackageItemRepository):
        self.package_item_repository = package_item_repository
        super().__init__(package_item_repository)
