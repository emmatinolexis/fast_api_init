from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.fuel_log_repository import FuelLogRepository
from app.schema.fuel_log_schema import (
    FleetManagerFuelLog,
    FuelLogCreateSchema,
    FuelLogSchema,
    SingleFuelLog,
    SingleFuelLogSchema,
)
from app.service.base_service import BaseService
from app.util.utils import load_bulk_fuel_logs_from_csv


class FuelLogService(BaseService):
    def __init__(
        self, fuel_log_repository: FuelLogRepository, asset_repository: AssetRepository
    ):
        self.fuel_log_repository = fuel_log_repository
        self.asset_repository = asset_repository
        super().__init__(fuel_log_repository)

    def create_individual_fuel_log(
        self, payload: FuelLogSchema, user_uuid: str, business_profile_uuid: str = None
    ):
        assigned_asset = self.asset_repository.get_asset_by_user_uuid(user_uuid)

        if not assigned_asset:
            raise NotFoundError(detail=messages.MUST_BE_ASSIGNED)

        log_payload = FuelLogCreateSchema(
            amount=payload.amount,
            quantity=payload.quantity,
            user_uuid=user_uuid,
            asset_uuid=assigned_asset.asset_uuid if assigned_asset else None,
            business_profile_uuid=business_profile_uuid,
            receipt_image=payload.receipt_image,
        )

        return self.fuel_log_repository.create(log_payload)

    def create_bulk_fuel_logs(
        self, user_uuid: str, csv_url: str, business_profile_uuid: str = None
    ):
        try:
            data = load_bulk_fuel_logs_from_csv(csv_url)
            for item in data:
                log_payload = FleetManagerFuelLog(
                    amount=item.get("amount"),
                    quantity=item.get("litres"),
                    purchase_date=item.get("purchase_date"),
                    driver_name=item.get("driver_name"),
                    asset_name=item.get("asset_name"),
                    business_profile_uuid=business_profile_uuid,
                    user_uuid=user_uuid,
                )
                self.fuel_log_repository.create(log_payload)

        except Exception as e:
            raise e

    def create_fleet_manager_single_fuel_log(
        self, payload: SingleFuelLog, user_uuid: str, business_profile_uuid: str = None
    ):
        full_payload = SingleFuelLogSchema(
            asset_uuid=payload.asset_uuid,
            amount=payload.amount,
            quantity=payload.quantity,
            purchase_date=payload.purchase_date,
            receipt_image=payload.receipt_image,
            user_uuid=user_uuid,
            business_profile_uuid=business_profile_uuid,
        )

        return self.fuel_log_repository.create(full_payload)
