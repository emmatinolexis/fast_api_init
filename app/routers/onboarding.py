from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.onboarding import (
    create_onboarding,
    delete_onboarding,
    get_all_onboardings,
    get_onboarding,
    update_onboarding,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/onboarding",
    tags=["onboarding"],
)


@router.get("/", response_model=None)
async def get_all_onboardings_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_onboardings(db)


@router.post("/create", response_model=schemas.Onboarding)
async def create_onboarding_handler(
    onboarding: schemas.Onboarding,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_onboarding(db, onboarding)


@router.put("/update/{uuid}", response_model=schemas.Onboarding)
async def update_onboarding_handler(
    uuid: str,
    onbaording: schemas.Onboarding,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return update_onboarding(
        db, uuid, model=schemas.Onboarding, onboarding_data=onbaording
    )


@router.get("/{uuid}", response_model=schemas.Onboarding)
async def get_onboarding_by_uuid_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return get_onboarding(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.Onboarding)
async def delete_onbaording_handler(
    uuid: str,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return delete_onboarding(db, uuid)
