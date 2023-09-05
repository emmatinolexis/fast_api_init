from fastapi import APIRouter

router = APIRouter(
    prefix="/system",
    tags=["system"],
)

@router.get("/health")
async def health_check():
    return {
        "status": "available",
        "version": "0.0.1",
    }