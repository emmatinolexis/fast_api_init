from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.driver_repository import DriverRepository
from app.repository.fuel_log_repository import FuelLogRepository
from app.schema.fuel_log_schema import (
    FleetManagerFuelLog,
    FuelLogCreateSchema,
    FuelLogSchema,
    SingleFuelLog,
    SingleFuelLogSchema,
)
from app.service.base_service import BaseService
from app.transfomers.fuel_log_transformer import fuel_log_transformer
from app.util.utils import load_bulk_fuel_logs_from_csv


class FuelLogService(BaseService):
    def __init__(
        self,
        fuel_log_repository: FuelLogRepository,
        asset_repository: AssetRepository,
        driver_repository: DriverRepository,
    ):
        self.fuel_log_repository = fuel_log_repository
        self.asset_repository = asset_repository
        self.driver_repository = driver_repository
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
            with self.fuel_log_repository.session_factory() as session:
                data = load_bulk_fuel_logs_from_csv(csv_url)
                fuel_logs = []  # Accumulate all fuel logs here

                for item in data:
                    driver_email = item.get("driver_email")
                    driver_details = self.driver_repository.get_driver_by_email(
                        driver_email
                    )
                    if not driver_details:
                        raise NotFoundError(
                            detail=messages.WRONG_DRIVER_EMAIL + driver_email
                        )

                    drivers_asset = self.asset_repository.get_asset_by_driver_email(
                        driver_email
                    )
                    if not drivers_asset:
                        raise NotFoundError(
                            detail=messages.DRIVER_NOT_ASSIGNED.format(driver_email)
                        )

                    log_payload = FleetManagerFuelLog(
                        amount=item.get("amount"),
                        quantity=item.get("litres"),
                        purchase_date=item.get("purchase_date"),
                        asset_name=drivers_asset.asset_name,
                        asset_uuid=drivers_asset.uuid,
                        business_profile_uuid=business_profile_uuid,
                        user_uuid=user_uuid,
                    )

                    fuel_logs.append(log_payload)  # Accumulate the log payload

                # Only after successful validation, perform bulk insert
                for log in fuel_logs:
                    self.fuel_log_repository.create(log)

                session.commit()  # Commit the transaction only if no errors occur
        except (NotFoundError, Exception) as e:
            if session:
                session.rollback()  # Rollback the transaction
            raise e

    def create_fleet_manager_single_fuel_log(
        self, payload: SingleFuelLog, user_uuid: str, business_profile_uuid: str = None
    ):
        asset = self.asset_repository.read_by_uuid(payload.asset_uuid)
        if not asset:
            raise NotFoundError(detail=messages.ASSET_NOT_FOUND)

        driver = self.asset_repository.get_driver_by_asset_uuid(payload.asset_uuid)

        if not driver:
            raise NotFoundError(detail=messages.ASSET_MUST_BE_ASSIGNEDD)

        full_payload = SingleFuelLogSchema(
            asset_uuid=payload.asset_uuid,
            amount=payload.amount,
            quantity=payload.quantity,
            purchase_date=payload.purchase_date,
            receipt_image=payload.receipt_image,
            user_uuid=user_uuid,
            business_profile_uuid=business_profile_uuid,
            driver_uuid=driver.uuid,
            payment_method=payload.payment_method,
            asset_name=asset.asset_name,
        )

        fuel_log = self.fuel_log_repository.create(full_payload)

        return fuel_log_transformer(fuel_log, self.driver_repository)

    def get_fuel_logs_by_user_uuid(
        self,
        user_uuid: str,
        page: int = 1,
        page_size: int = 10,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        try:
            fuel_logs = self.fuel_log_repository.get_fuel_logs_by_user_uuid(
                user_uuid, search, start_date, end_date
            )

            total = len(fuel_logs)
            paginated_fuel_logs = fuel_logs[(page - 1) * page_size : page * page_size]

            return {
                "total": total,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total // page_size + 1,
                "data": [
                    fuel_log_transformer(log, self.driver_repository)
                    for log in paginated_fuel_logs
                ],
            }
        except Exception as e:
            raise e

    def get_fuel_logs_by_business_uuid(
        self,
        business_uuid: str,
        page: int = 1,
        page_size: int = 10,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        try:
            fuel_logs = self.fuel_log_repository.get_fuel_logs_by_business_uuid(
                business_uuid, search, start_date, end_date
            )

            total = len(fuel_logs)
            paginated_fuel_logs = fuel_logs[(page - 1) * page_size : page * page_size]

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total // page_size + 1,
                "data": [
                    fuel_log_transformer(log, self.driver_repository)
                    for log in paginated_fuel_logs
                ],
            }
        except Exception as e:
            raise e

    def update_fuel_log_receipt(self, fuel_log_uuid: str, payload: SingleFuelLog):
        updated_fuel_log = self.fuel_log_repository.update_attr_by_uuid(
            fuel_log_uuid, "receipt_image", payload.receipt_image
        )

        return fuel_log_transformer(updated_fuel_log)

    def get_receipt_by_uuid(self, fuel_log_uuid: str):
        fuel_log = self.fuel_log_repository.read_by_uuid(fuel_log_uuid)
        return fuel_log_transformer(fuel_log)
