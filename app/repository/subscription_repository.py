from contextlib import AbstractContextManager
from typing import Callable, List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.model.package import Package
from app.model.subscription import Subscription
from app.model.user import User
from app.repository.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Subscription)

    def read_all_subscriptions_(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(Subscription.user))
                .options(joinedload(Subscription.package))
                .all()
            )

    def read_all_subscriptions(
        self, page=1, page_size=10
    ) -> Tuple[List[Subscription], int]:
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            query = session.query(self.model)
            total_subscription = query.count()

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            subscriptions = (
                query.options(
                    joinedload(Subscription.user).joinedload(User.business_profile)
                )
                .options(
                    joinedload(Subscription.package).joinedload(
                        Package.package_item_assignments
                    )
                )
                .all()
            )

            return subscriptions, total_subscription
