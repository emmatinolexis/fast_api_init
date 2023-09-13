from fastapi import APIRouter

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

@router.get("/health")
async def health_check():
    return {
        "name": "MV Tracking Hub",
        "version": "0.0.1",
        "status": "available",
    }
