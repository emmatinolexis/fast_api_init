from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext import AsynSession, joinedload

from app.model.package_item_assignment import PackageItemAssignment
from app.repository.base_repository import BaseRepository


class PackageItemAssignmentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, PackageItemAssignment)

    def get_all_package_items(self, plan_code):
        with self.session_factory() as session:
            return (
                session.query(PackageItemAssignment)
                .filter(PackageItemAssignment.paystack_plan_code == plan_code)
                .options(joinedload(PackageItemAssignment.package_item))
                .all()
            )
