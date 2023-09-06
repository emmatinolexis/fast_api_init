from fastapi import APIRouter

router = APIRouter(
    prefix="/dummy",
    tags=["users"],
)


@router.get("/info")
async def get_info():
    return {
        "msg": "dummy data",
        "action": "Tariq & Rudolph to remove me later",
    }