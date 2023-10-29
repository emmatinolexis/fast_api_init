from fastapi import APIRouter,Depends
from app.utils.auth import get_current_user
from app.database import schemas

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

@router.get("/health")
async def health_check(get_current_user: schemas.User = Depends(get_current_user)):
    return {
        "name": "MV Tracking Hub",
        "version": "0.0.1",
        "status": "available",
    }
