from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.util.enums import ActiveStatus, SubscriptionPeriod, SubscriptionTypes


class SubscriptionPayload(BaseModel):
    subscription_type: SubscriptionTypes
    subscription_period: SubscriptionPeriod
    start_date: date
    end_date: date
    subscription_amount: int
    user_uuid: UUID
    package_uuid: UUID
    status: ActiveStatus

    class Config:
        orm_model = True


class UpdateUserSubscriptionPayload(BaseModel):
    business_uuid: Optional[UUID] = None
    user_uuid: UUID
    package_uuid: UUID
    payment_uuid: Optional[UUID] = None
    subscription_period: SubscriptionPeriod
    subscription_type: SubscriptionTypes
    start_date: date
    end_date: date

    class Config:
        orm_model = True
