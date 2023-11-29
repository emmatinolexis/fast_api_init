# from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.alert_policy import (  # delete_alert_policy,; update_alert_policy,
    create_alert_policy,
    get_all_alert_policies,
)
from app.utils.auth import get_current_user

from .shared import get_db

router = APIRouter(
    prefix="/alert_policies",
    tags=["alert_policy"],
)


@router.get("/", response_model=None)
async def get_alert_policies_handler(
    db: Session = Depends(get_db), auth_user: schemas.User = Depends(get_current_user)
):
    return get_all_alert_policies(db)


@router.post("/create", response_model=None)
async def create_alert_policy_handler(
    alert_policy: schemas.AlertPolicy,
    db: Session = Depends(get_db),
    auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_policy(db=db, alert_policy=alert_policy)


# @router.put("/update/{uuid}", response_model=schemas.AlertPolicy)
# async def update_alert_policy_handler(
#     uuid: str,
#     updated_alert_policy: schemas.AlertPolicy,
#     db: Session = Depends(get_db),
#     auth_user: schemas.User = Depends(get_current_user),
# ):
#     return update_alert_policy(
#         db,
#         uuid,
#         model=models.AlertPolicy,
#         updated_alert_policy=updated_alert_policy,
#     )


# @router.delete("/delete/{uuid}", response_model=schemas.AlertPolicy)
# async def delete_alert_policy_by_uuid_handler(
#     uuid: str,
#     db: Session = Depends(get_db),
#     auth_user: schemas.User = Depends(get_current_user),
# ):
#     return delete_alert_policy(db, uuid)
