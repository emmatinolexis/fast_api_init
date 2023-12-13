from typing import Union

from fastapi import APIRouter
from app.util.utils import allow_admins_only

router = APIRouter(
    prefix="/tracking",
    tags=["tracking"],
)


@router.post("/",dependencies=[allow_admins_only])
async def get_tracker_details(data: Union[str, list, dict]):
    return {"data": data}
