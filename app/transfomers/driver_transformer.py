from app.model.user import User as Driver
from app.repository.asset_repository import AssetRepository
from app.transfomers.asset_transformer import asset_transformer









def driver_transformer(driver:Driver,asset_repo:AssetRepository):

    driver_asset = asset_repo.read_by_uuid(driver.assigned_asset_uuid)

    return {
        "fullname": f"{driver.first_name} {driver.last_name}",
        "email": driver.email_address,
        "phone_number":driver.phone_number,
        "operator_type":driver.operator_type,
        "profile_picture":driver.avatar_url,
        "asset": asset_transformer(driver_asset) if driver.assigned_asset_uuid else None
    }