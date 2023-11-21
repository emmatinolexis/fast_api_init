from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel


class TrackingDeviceCreate(BaseModel):
    data: Union[str, list, dict]


router = APIRouter(
    prefix="",
    tags=["tracking"],
)


@router.post("/")
async def get_tracker_details(data: Union[str, list, dict]):
    print(data)
