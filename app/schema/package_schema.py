from typing import List
from uuid import UUID

from pydantic import BaseModel


class GetPackage(BaseModel):
    uuid: str


class PackageItem(BaseModel):
    item_name: str
    status: str

    class Config:
        orm_model = True


class Package(BaseModel):
    package_name: str
    package_price: str
    package_description: str

    class Config:
        orm_model = True


class PackageItemAssignment(BaseModel):
    package_item_uuids: List[UUID]
    package_uuid: UUID

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
