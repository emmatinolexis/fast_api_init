from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from app.model.installation import Installation
from app.model.order import Order
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.installation_schema import InstallationPayload
from app.util.enums import CustomerRoles


class InstallationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, InstallationRepository)

    def get_installers(self):
        with self.session_factory() as session:
            return (
                session.query(User)
                .filter(User.user_role_uuid == CustomerRoles.INSTALLER)
                .all()
            )

    def create_installation(self, installation_payload: InstallationPayload):
        with self.session_factory() as session:
            try:
                existing_installation = session.query(Installation).filter_by(order_uuid=installation_payload.order_uuid).first()
                if existing_installation:
                    raise ValueError(f"Installation already exists for order UUID: {installation_payload.order_uuid}")

                installation = Installation(
                    installer_uuid=installation_payload.installer_uuid,
                    order_uuid=installation_payload.order_uuid,
                )
                session.add(installation)
                
                order = session.query(Order).filter_by(uuid=installation_payload.order_uuid).first()
                if order:
                    order.date_of_installation = installation_payload.date_of_installation
                    order.time_of_installation = installation_payload.time_of_installation
                
                session.commit()
                session.refresh(installation)
                return installation
            except Exception as e:
                session.rollback()
                raise e
                
