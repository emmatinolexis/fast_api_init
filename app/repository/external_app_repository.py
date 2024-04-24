from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.external_app import ExternalApp
from app.repository.base_repository import BaseRepository
from app.schema.external_app_schema import ExternalAppPayload


class ExternalAppRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ExternalApp)

    def create_external_app(self, payload: ExternalAppPayload) -> ExternalApp:
        with self.session_factory() as session:
            try:
                external_app = ExternalApp(
                    app_id=payload.app_id,
                    secret_key=payload.secret_key,
                    no_of_days_to_expire=payload.no_of_days_to_expire,
                )
                session.add(external_app)
                session.commit()
                session.refresh(external_app)
                return external_app
            except Exception as e:
                session.rollback()
                raise e
