from fastapi import APIRouter

dummy_options = ["Option" + str(i) for i in range(1, 11)]

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/packages")
async def get_product_packages():
    return {
        "packages": {
            "basic": dummy_options,
            "individual": dummy_options,
            "enterprise": dummy_options
        }
    }
    
