from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.fuel_log_repository import FuelLogRepository
from app.schema.fuel_log_schema import FuelLogCreateSchema, FuelLogSchema
from app.service.base_service import BaseService


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
