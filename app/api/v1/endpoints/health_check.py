from fastapi import APIRouter

from app.core.config import configs

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/")
async def health_check_handler():
    return {
        "name": configs.PROJECT_NAME,
        "version": configs.API_VERSION,
        "status": "ok",
    }
