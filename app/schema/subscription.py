from datetime import date
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
