from typing import Optional

from pydantic import BaseModel


class FuelLogSchema(BaseModel):
    amount: float
    quantity: float
    receipt_image: Optional[str] = None


class FuelLogCreateSchema(FuelLogSchema):
    user_uuid: str
    asset_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None
    receipt_image: Optional[str] = None
