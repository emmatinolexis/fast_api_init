from typing import List

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.assets import get_asset_type
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/asset_types",
    tags=["assets"],
)

@router.get("/", response_model=List[schemas.AssetType])
async def get_asset_type_handler(asset_type: Session = Depends(get_db),get_current_user: schemas.User = Depends(get_current_user)):
    return get_asset_type(asset_type)
