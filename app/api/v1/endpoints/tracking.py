from typing import Union

from fastapi import APIRouter

router = APIRouter(
    prefix="/tracking",
    tags=["tracking"],
)


@router.post("/")
async def get_tracker_details(data: Union[str, list, dict]):
    return {"data": data}
