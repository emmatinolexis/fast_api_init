from contextlib import AbstractContextManager
from datetime import datetime
from sqlalchemy import and_, or_
from typing import Callable
from sqlalchemy.orm import Session
from app.model.installation import Installation
from app.model.order import Order
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.installation_schema import InstallationPayload, AssignInstallerPayload
from app.util.enums import CustomerRoles
from sqlalchemy.orm import joinedload
from app.util.enums import InstallationStatus
from app.model.order import OrderDeviceAssignment
from app.util.utils import parse_date


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
                    joinedload(Installation.order).joinedload(Order.order_inventories).joinedload(
                        OrderDeviceAssignment.inventory),
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

    def assign_installer_to_installation(self, payload: AssignInstallerPayload):
        with self.session_factory() as session:
            installation = (
                session.query(self.model)
                .filter(self.model.uuid == payload.installation_uuid)
                .first()
            )
            installation.installer_uuid = payload.installer_uuid
            installation.assigned_at = datetime.now()
            session.commit()
            session.refresh(installation)
            return installation

    def update_installation_status(self, installation_uuid: str, status: InstallationStatus):
        with self.session_factory() as session:
            installation = (
                session.query(self.model)
                .filter(self.model.uuid == installation_uuid)
                .first()
            )
            installation.status = status
            installation.installed_at = datetime.now()
            session.commit()
            session.refresh(installation)
            return installation

    def get_installations(self,
                          page: int = 1,
                          per_page: int = 10,
                          installer_uuid: str = None,
                          status: InstallationStatus = None,
                          start_date: str = None,
                          end_date: str = None,
                          search_parameter: str = None):
        with self.session_factory() as session:
            # Build the base query with joinedload
            query = session.query(Installation).options(
                joinedload(Installation.order).joinedload(Order.order_inventories).joinedload(
                    OrderDeviceAssignment.inventory),
                joinedload(Installation.order).joinedload(Order.order_shipping_address),
                joinedload(Installation.installer)
            )

            # Filter by installer_uuid if provided
            if installer_uuid:
                query = query.filter(Installation.installer_uuid == installer_uuid)

            # Filter by status if provided
            if status:
                query = query.filter(Installation.status == status)

            # Filter by date range if provided
            if start_date:
                start_date = parse_date(start_date)
                query = query.filter(Installation.created_at >= start_date)

            if end_date:
                end_date = parse_date(end_date)
                query = query.filter(Installation.created_at <= end_date)

            # Apply date range filtering with and_
            if start_date and end_date:
                start_date_obj = parse_date(start_date)
                end_date_obj = parse_date(end_date)
                query = query.filter(
                    and_(
                        Installation.created_at >= start_date_obj,
                        Installation.created_at <= end_date_obj
                    )
                )
            elif start_date:
                start_date_obj = parse_date(start_date)
                query = query.filter(Installation.created_at >= start_date_obj)
            elif end_date:
                end_date_obj = parse_date(end_date)
                query = query.filter(Installation.created_at <= end_date_obj)

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
