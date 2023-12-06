from uuid import UUID

from pydantic import BaseModel


class FeatureInput(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str

    class Config:
        orm_model = True


class Feature(BaseModel):
    feature_name: str
    feature_description: str
    icon_url: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True
