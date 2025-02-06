from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.orm import AsynSession

from app.model.subscription_payment import SubscriptionPayment
from app.repository.base_repository import BaseRepository


class SubscriptionPaymentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, SubscriptionPayment)
