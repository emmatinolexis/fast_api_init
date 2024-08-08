from app.model.fuel_log import FuelLog


def fuel_log_transformer(fuel_log: FuelLog):
    return {
        "uuid": fuel_log.fuel_log_id,
        "amount": fuel_log.amount,
        "quantity": fuel_log.quantity,
        "user_uuid": fuel_log.user_uuid,
        "business_profile_uuid": fuel_log.business_profile_uuid
        if fuel_log.business_profile_uuid
        else None,
        "asset_uuid": fuel_log.asset_uuid if fuel_log.asset_uuid else None,
        "asset_name": fuel_log.asset_name,
        "driver_name": fuel_log.driver_name,
        "receipt_image": fuel_log.receipt_image if fuel_log.receipt_image else None,
        "purchase_date": fuel_log.purchase_date if fuel_log.purchase_date else None,
        "created_at": fuel_log.created_at,
    }
