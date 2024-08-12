from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import FuelLogPaymmentMethod


class FuelLogSchema(BaseModel):
    amount: float
    quantity: float
    receipt_image: Optional[str] = None


class FuelLogCreateSchema(FuelLogSchema):
    user_uuid: str
    asset_uuid: Optional[str] = None
    business_profile_uuid: Optional[str] = None
    receipt_image: Optional[str] = None


class FleetManagerFuelLog(BaseModel):
    amount: float
    quantity: float
    purchase_date: Optional[str] = None
    asset_name: str
    business_profile_uuid: Optional[str] = None
    user_uuid: str
    asset_uuid: str
    driver_uuid: str


class SingleFuelLog(BaseModel):
    asset_uuid: str
    amount: float
    quantity: float
    purchase_date: date
    payment_method: FuelLogPaymmentMethod
    receipt_image: str


class SingleFuelLogSchema(SingleFuelLog):
    user_uuid: UUID
    driver_uuid: Optional[UUID] = None
    business_profile_uuid: Optional[str] = None
    asset_name: Optional[str] = None


class UpdateFuelLog(BaseModel):
    receipt_image: str
