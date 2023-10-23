from fastapi import APIRouter
from fastapi import Depends
from app.database import schemas
from app.utils.auth import get_current_user

 
dummy_options = ["Option" + str(i) for i in range(1, 11)]

router = APIRouter(
    prefix="/packages",
    tags=["packages"],
)

@router.get("/")
async def get_product_packages(get_current_user: schemas.User = Depends(get_current_user)):
    return {
        "packages": {
            "basic": dummy_options,
            "individual": dummy_options,
            "enterprise": dummy_options
        }
    }
    
