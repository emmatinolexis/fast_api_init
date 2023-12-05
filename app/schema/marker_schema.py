from uuid import UUID

from pydantic import BaseModel


class MarkerIcon(BaseModel):
    icon_name: str
    icon_url: str
    status: str


class MarkerIconFetch(BaseModel):
    icon_name: str
    icon_url: str
    status: str
    uuid: UUID

    class Config:
        orm_model = True
