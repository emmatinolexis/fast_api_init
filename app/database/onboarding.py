from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.utils.enums import AccountType

from . import models, schemas
from .helpers import (
    create_item,
    delete_item,
    get_all_items,
    get_item_by_id,
    update_item,
)


def get_all_onboardings(db: Session):
    try:
        onboardings = get_all_items(db, models.Onboarding)
        return onboardings
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_individual_onboarding(db: Session, onboarding: schemas.Onboarding):
    try:
        onboarding_item = {
            "asset_type_uuid": onboarding.asset_type_uuid,
            "number_of_assets": onboarding.number_of_assets,
            "number_of_months": onboarding.number_of_months,
            "package_uuid": onboarding.package_uuid,
            "user_uuid": onboarding.user_uuid,
            "onboarding_type": AccountType.INDIVIDUAL,
        }

        create_onboarding = create_item(db, models.Onboarding, onboarding_item)

        for item in onboarding.features_uuid:
            feature = {"onboarding_uuid": create_onboarding.uuid, "feature_uuid": item}

            create_item(db, models.OnboardingFeatureAssignment, feature)

        return onboarding_item

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def create_business_onboarding(db: Session, onboarding: schemas.BusinessOnboarding):
    try:
        # create onboarding
        onboarding_data = {
            "asset_type_uuid": onboarding.asset_type_uuid,
            "number_of_assets": onboarding.number_of_assets,
            "user_uuid": onboarding.user_uuid,
            "onboarding_type": AccountType.ORGANISATION,
        }

        create_onboarding = create_item(db, models.Onboarding, onboarding_data)

        # assign features to onboarding
        for item in onboarding.features_uuid:
            feature = {"onboarding_uuid": create_onboarding.uuid, "feature_uuid": item}
            create_item(db, models.OnboardingFeatureAssignment, feature)

        # create business
        business_data = {
            "business_name": onboarding.business_name,
            "business_email": onboarding.business_email,
            "business_phone": onboarding.business_phone,
            "business_location": onboarding.business_location,
            "business_address": onboarding.business_address,
            "business_logo": onboarding.business_logo,
        }
        create_business = create_item(db, models.BusinessProfile, business_data)

        # assign user to business
        assignment_data = {
            "user_uuid": onboarding.user_uuid,
            "business_profile_uuid": create_business.uuid,
        }
        create_item(db, models.UserOrganisationAssignment, assignment_data)

        return onboarding

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def update_onboarding(
    db: Session,
    onboarding_uuid: str,
    model: models.Onboarding,
    onboarding_data: schemas.Onboarding,
):
    try:
        onboarding_item = {
            "asset_type_uuid": onboarding_data.asset_type_uuid,
            "number_of_assets": onboarding_data.number_of_assets,
            "number_of_months": onboarding_data.number_of_months,
            "package_uuid": onboarding_data.package_uuid,
            "user_uuid": onboarding_data.user_uuid,
        }
        return onboarding_uuid
        update_item(db, onboarding_uuid, model, onboarding_item)
        return onboarding_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def delete_onboarding(db: Session, uuid: str):
    try:
        return delete_item(db, models.Onboarding, uuid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


def get_onboarding(db: Session, uuid: str):
    try:
        package = get_item_by_id(db, model=models.Onboarding, uuid=uuid)
        return package
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
