from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext import AsynSession

from app.model.user_organisation_assignment import UserOrganisationAssignment
from app.repository.base_repository import BaseRepository


class UserOrganisationAssignmentRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, UserOrganisationAssignment)
