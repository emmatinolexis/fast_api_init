from app.repository.package_item_assignments_repository import (
    PackageItemAssignmentRepository,
)
from app.service.base_service import BaseService


class PackageItemAssignmentService(BaseService):
    def __init__(
        self, package_item_assignments_repository: PackageItemAssignmentRepository
    ):
        self.package_item_assignments_repository = package_item_assignments_repository
        super().__init__(package_item_assignments_repository)

    def get_package_items(self, plan_code: str):
        try:
            package_items = (
                self.package_item_assignments_repository.get_all_package_items(
                    plan_code
                )
            )
            return package_items
        except Exception as e:
            raise e
