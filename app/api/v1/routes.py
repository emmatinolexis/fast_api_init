from fastapi import APIRouter

from app.api.v1.endpoints.authentication import router as auth_router
from app.api.v1.endpoints.health_check import router as health_check_router
from app.api.v1.endpoints.permission import router as permission_router
from app.api.v1.endpoints.users import router as users_router


routers = APIRouter()
router_list = [
    health_check_router,
    auth_router,
    users_router,
    permission_router,
]

for router in router_list:
    routers.include_router(router)
