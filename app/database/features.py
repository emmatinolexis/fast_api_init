from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .helpers import (create_item, delete_item, get_all_items, get_item_by_id,
                      update_item)

# CRUD functionalities for features


def get_all_features(db: Session):
    features = get_all_items(db, models.Feature)
    if features:
        return features
    raise HTTPException(status_code=404, detail="Feature Not Found")


def create_feature(db: Session, feature: schemas.Feature):
    feature_data = {
        "feature_name": feature.feature_name,
        "feature_description": feature.feature_description,
        "icon_url": feature.icon_url,
        "status": feature.status,
    }
    create_item(db, models.Feature, feature_data)
    if create_feature:
        return feature_data
    raise HTTPException(status_code=500, detail="Error creating feature")


def update_feature(
    db: Session,
    feature_uuid: str,
    model: models.Feature,
    updated_feature: schemas.Feature,
):
    updated_feature_data = {
        "feature_name": updated_feature.feature_name,
        "feature_description": updated_feature.feature_description,
        "icon_url": updated_feature.icon_url,
        "status": updated_feature.status,
    }
    updated = update_item(db, feature_uuid, model, updated_feature_data)
    if updated:
        return updated
    raise HTTPException(status_code=500, detail="Error Updating feature")


def delete_feature(db: Session, uuid: str):
    return delete_item(db, models.Feature, uuid)


def get_feature_by_uuid(db: Session, uuid: str):
    feature = get_item_by_id(db, model=models.Feature, uuid=uuid)
    if feature:
        return feature
    raise HTTPException(status_code=404, detail="feature not found")
