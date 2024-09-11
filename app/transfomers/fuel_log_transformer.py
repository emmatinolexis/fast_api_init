from app.model.fuel_log import FuelLog
from app.repository.driver_repository import DriverRepository


def fuel_log_transformer(fuel_log: FuelLog, driver_repo: DriverRepository):
    driver = driver_repo.read_by_uuid(fuel_log.driver_uuid)

    driver_details = {
        "uuid": driver.uuid if driver else None,
        "full_name": f"{driver.first_name} {driver.last_name}" if driver else None,
        "phone_number": driver.phone_number if driver else None,
        "email": driver.email if driver else None,
        "profile_image": driver.profile_picture_url if driver else None,
    }

    return {
        "uuid": fuel_log.uuid,
        "amount": fuel_log.amount,
        "quantity": fuel_log.quantity,
        "user_uuid": fuel_log.user_uuid,
        "business_profile_uuid": fuel_log.business_profile_uuid
        if fuel_log.business_profile_uuid
        else None,
        "asset_uuid": fuel_log.asset_uuid if fuel_log.asset_uuid else None,
        "asset_name": fuel_log.asset_name,
        "receipt_image": fuel_log.receipt_image if fuel_log.receipt_image else None,
        "purchase_date": fuel_log.purchase_date if fuel_log.purchase_date else None,
        "payment_method": fuel_log.payment_method,
        "fuel_type": fuel_log.fuel_type if fuel_log.fuel_type else None,
        "created_at": fuel_log.created_at,
        "driver_details": driver_details,
    }
