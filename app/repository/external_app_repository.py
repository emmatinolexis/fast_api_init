from typing import Callable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.external_app import ExternalApp
from app.repository.base_repository import BaseRepository
from app.schema.external_app_schema import (
    ExternalAppGenerateTokenPayload,
    ExternalAppPayload,
)
from app.util.enums import ActiveStatus


class ExternalAppRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, ExternalApp)

    async def create_external_app(self, payload: ExternalAppPayload) -> ExternalApp:
        async with self.session_factory() as session:
            try:
                external_app = ExternalApp(
                    app_id=payload.app_id,
                    secret_key=payload.secret_key,
                    no_of_days_to_expire=payload.no_of_days_to_expire,
                )
                session.add(external_app)
                await session.commit()
                await session.refresh(external_app)
                return external_app
            except Exception as e:
                await session.rollback()
                raise e

    async def get_app_service(
        self, payload: ExternalAppGenerateTokenPayload
    ) -> ExternalApp:
        async with self.session_factory() as session:
            try:
                query = (
                    select(self.model)
                    .filter(self.model.app_id == payload.app_id)
                    .filter(self.model.secret_key == payload.secret_key)
                )
                result = await session.execute(query)
                app = result.scalar_.one_or_none()

                if not app:
                    raise Exception("Invalid app_id or secret_key")
                if app.status == ActiveStatus.INACTIVE:
                    raise Exception(
                        "Your access has been revoked, contact administrator"
                    )
                return app
            except Exception as e:
                raise e

    async def get_app_service_by_secret_key(
        self, secret_key: str
    ) -> Optional[ExternalApp]:
        async with self.session_factory() as session:
            try:
                query = select(self.model).filter(self.model.secret_key == secret_key)
                result = await session.execute(query)
                return result.scalar_.one_or_none()
            except Exception as e:
                raise e
