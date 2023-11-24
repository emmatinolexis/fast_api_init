from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import schemas
from app.database.alert_recipient import (  # get_alert_recipient_by_uuid,; get_all_alert_recipients,; update_alert_recipient,
    create_alert_recipient,
    delete_alert_recipient,
)

from .shared import get_db

# from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/alert_recipients",
    tags=["alert_recipients"],
)


# @router.get("/", response_model=list[schemas.AlertRecipient])
# async def get_all_alert_recipients_handler(
#     db: Session = Depends(get_db),
#     # auth_user: schemas.User = Depends(get_current_user)
# ):
#     return get_all_alert_recipients(db)


@router.post("/create", response_model=schemas.AlertRecipient)
async def create_alert_recipient_handler(
    recipients: schemas.AlertRecipient,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return create_alert_recipient(db, recipients)


# @router.put("/update/{uuid}", response_model=schemas.AlertRecipient)
# async def update_alert_recipient_handler(
#     uuid: str,
#     updated_alert_recipient: schemas.AlertRecipient,
#     db: Session = Depends(get_db),
#     # auth_user: schemas.User = Depends(get_current_user),
# ):
#     return update_alert_recipient(
#         db,
#         uuid,
#         model=models.AlertRecipient,
#         updated_alert_recipient=updated_alert_recipient
#     )


# @router.get("/{uuid}", response_model=schemas.AlertRecipient)
# async def get_alert_recipient_by_uuid_handler(
#     uuid: str,
#     db: Session = Depends(get_db),
#     # auth_user: schemas.User = Depends(get_current_user),
# ):
#     return get_alert_recipient_by_uuid(db, uuid)


@router.delete("/delete/{uuid}", response_model=schemas.AlertRecipient)
async def delete_alert_recipient_handler(
    uuid: str,
    db: Session = Depends(get_db),
    # auth_user: schemas.User = Depends(get_current_user),
):
    return delete_alert_recipient(db, uuid)
