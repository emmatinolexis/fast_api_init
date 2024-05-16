from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus


class GetPackage(BaseModel):
    uuid: str


class PackageItemPayload(BaseModel):
    item_name: str
    status: ActiveStatus

    class Config:
        orm_model = True


class PackagePayload(BaseModel):
    package_name: str
    package_price: str
    package_description: str

    class Config:
        orm_model = True


class PackageItemAssignmentPayload(BaseModel):
    package_item_uuids: List[UUID]
    package_plan_code: str

    class Config:
        orm_model = True


class PackageItemAssignmentInput(BaseModel):
    package_uuid: UUID
    package_plan_code: str

    class Config:
        orm_model = True


class PaystackPackagePlanPayload(BaseModel):
    name: str
    amount: int
    description: str

    class Config:
        orm_model = True


class PackageOutput(BaseModel):
    package_name: str
    package_price: str
    package_description: str
    uuid: UUID
    # package_item:PackageItemAssignment

    class Config:
        orm_model = True
