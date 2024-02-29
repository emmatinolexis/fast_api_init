from sqlalchemy import exc

from app.core.exceptions import NotFoundError
from app.repository.package_repository import PackageRepository
from app.schema.package_schema import (
    PackageItemAssignmentPayload,
    PaystackPackagePlanPayload,
)
from app.service.base_service import BaseService


class PackageService(BaseService):
    def __init__(self, package_repository: PackageRepository):
        self.package_repository = package_repository
        super().__init__(package_repository)

    def get_all_paystack_plans(self):
        try:
            packages = self.package_repository.get_all_paystack_plans()
            return packages
        except Exception as e:
            raise e

    def get_paystack_plan(self, plan_code: str):
        try:
            package = self.package_repository.read_by_plan_code(plan_code)
            return package
        except Exception as e:
            raise e

    def update_paystack_plan(self, plan_code, plan_data: PaystackPackagePlanPayload):
        try:
            package = self.package_repository.update_paystack_plan(plan_code, plan_data)
            return package
        except Exception as e:
            raise e

    def create_paystack_package_plan(self, payload: PaystackPackagePlanPayload):
        try:
            package = self.package_repository.create_paystack_package_plan(payload)
            return package
        except Exception as e:
            raise e

    def get_all_packages(self):
        try:
            packages = self.package_repository.get_all_packages()
            return packages
        except Exception as e:
            raise e

    def assign_package_item(self, payload: PackageItemAssignmentPayload):
        try:
            if (
                self.package_repository.read_by_plan_code(payload.package_plan_code)
                is None
            ):
                raise NotFoundError(detail=payload.package_plan_code)
            self.package_repository.assign_package_item(payload)
        except exc.IntegrityError as e:
            raise e
        except Exception as e:
            raise e

    def delete_package_item(self, plan_code: str, package_item_uuid: str):
        try:
            if self.package_repository.read_by_plan_code(plan_code) is None:
                raise NotFoundError(detail=plan_code)

            db_item = self.package_repository.delete_package_item(
                plan_code, package_item_uuid
            )
            return db_item
        except Exception as e:
            raise e
