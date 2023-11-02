from typing import List
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from .shared import get_db

from app.database.features import (
    get_all_features,
    create_feature,
    update_feature,
    delete_feature,
    get_feature_by_uuid
)

from app.database import models,schemas
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/features",
    tags=["features"],
)

@router.get("/", response_model=List[schemas.Feature])
async def get_all_features_handler(db: Session = Depends(get_db),  auth_user: schemas.User = Depends(get_current_user)):
    return get_all_features(db)
    
@router.post("/create", response_model=None)
async def create_feature_handler(feature:schemas.Feature, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return create_feature(db=db, feature=feature)

@router.put("/update/{uuid}", response_model=schemas.Feature)
async def update_feature_handler(uuid:str, feature:schemas.Feature, db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return update_feature(db,uuid,model=models.Feature,updated_feature=feature)

@router.get("/{uuid}", response_model=schemas.Feature)
async def get_feature_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return get_feature_by_uuid(db,uuid)

@router.delete("/delete/{uuid}", response_model=schemas.Feature)
async def delete_feature_by_uuid_handler(uuid:str,db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)):
    return delete_feature(db,uuid)
