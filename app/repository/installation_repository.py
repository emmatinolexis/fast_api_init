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
from sqlalchemy.orm import joinedload
from app.util.enums import InstallationStatus


class InstallationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Installation)

    def get_installers(self):
        with self.session_factory() as session:
            return (
                session.query(User)
                .filter(User.user_role_uuid == CustomerRoles.INSTALLER)
                .all()
            )

    def get_installation(self, installation_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.uuid == installation_uuid)
                .options(
                    joinedload(Installation.order).joinedload(Order.order_shipping_address),
                    joinedload(Installation.installer)
                ).first()
            )

    def get_installation_by_order_uuid(self, order_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.order_uuid == order_uuid)
                .options(
                    joinedload(Installation.order).joinedload(Order.order_shipping_address),
                    joinedload(Installation.installer)
                ).first()
            )

    def get_installations(self, page: int = 1, per_page: int = 10):
        with self.session_factory() as session:
            # Build the query with joinedload
            query = (
                session.query(Installation)
                .options(
                    joinedload(Installation.order).joinedload(Order.order_shipping_address),
                          joinedload(Installation.installer)
                )
            )

            # Get total number of records for pagination metadata
            total_records = query.count()
            total_pages = (total_records + per_page - 1) // per_page

            # Apply pagination
            paginated_query = query.limit(per_page).offset((page - 1) * per_page)
            installations = paginated_query.all()

            return {
                "data": installations,
                "current_page": page,
                "page_size": per_page,
                "total_records": total_records,
                "total_pages": total_pages
            }

    def create_installation(self, installation_payload: InstallationPayload):
        with self.session_factory() as session:
            try:
                installation = Installation(
                    order_uuid=installation_payload.order_uuid,
                )
                session.add(installation)

                order = (
                    session.query(Order)
                    .filter_by(uuid=installation_payload.order_uuid)
                    .first()
                )
                if order:
                    order.date_of_installation = (
                        installation_payload.date_of_installation
                    )
                    order.time_of_installation = (
                        installation_payload.time_of_installation
                    )

                session.commit()
                session.refresh(installation)
                return installation
            except Exception as e:
                session.rollback()
                raise e
