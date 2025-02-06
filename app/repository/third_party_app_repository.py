from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext import AsynSession

from app.model.third_party_app import ThirdPartyApp
from app.repository.base_repository import BaseRepository


class ThirdPartyAppRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, ThirdPartyApp)
