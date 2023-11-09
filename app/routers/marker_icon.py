from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import models, schemas
from app.database.marker_icon import (  # delete_marker_icon,
    create_marker_icon,
    get_all_marker_icons,
    get_marker_icon_by_uuid,
    update_marker_icon,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/marker_icons",
    tags=["marker_icons"],
)


@router.get("/", response_model=list[schemas.MarkerIcon])
async def get_all_marker_icons_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_marker_icons(db)


@router.post("/create", response_model=None)
async def create_marker_icon_handler(
    icon: schemas.MarkerIcon,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_marker_icon(db, icon)


@router.put("/update/{uuid}", response_model=None)
async def update_marker_icon_handler(
    uuid: str,
    icon: schemas.MarkerIcon,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_marker_icon(
        db=db, uuid=uuid, model=models.MarkerIcon, updated_icon=icon
    )


@router.get("/{uuid}", response_model=schemas.MarkerIcon)
async def get_marker_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return get_marker_icon_by_uuid(db, uuid)
