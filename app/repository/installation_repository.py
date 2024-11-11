from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.model.installation import Installation
from app.model.order import Order, OrderDeviceAssignment
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.installation_schema import AssignInstallerPayload, InstallationPayload
from app.util.enums import CustomerRoles, InstallationStatus
from app.util.utils import calculate_percentage_change, parse_date


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
                    joinedload(Installation.order)
                    .joinedload(Order.order_inventories)
                    .joinedload(OrderDeviceAssignment.inventory),
                    joinedload(Installation.order).joinedload(
                        Order.order_shipping_address
                    ),
                    joinedload(Installation.installer),
                )
                .first()
            )

    def get_installation_by_order_uuid(self, order_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.order_uuid == order_uuid)
                .options(
                    joinedload(Installation.order).joinedload(
                        Order.order_shipping_address
                    ),
                    joinedload(Installation.installer),
                )
                .first()
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

    def update_installation_status(
        self, installation_uuid: str, status: InstallationStatus
    ):
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

    def get_installations(
        self,
        page: int = 1,
        per_page: int = 10,
        installer_uuid: str = None,
        status: InstallationStatus = None,
        start_date: str = None,
        end_date: str = None,
    ):
        with self.session_factory() as session:
            # Build the base query with joinedload
            query = session.query(Installation).options(
                joinedload(Installation.order)
                .joinedload(Order.order_inventories)
                .joinedload(OrderDeviceAssignment.inventory),
                joinedload(Installation.order).joinedload(Order.order_shipping_address),
                joinedload(Installation.installer),
            )

            # Filter by installer_uuid if provided
            if installer_uuid:
                query = query.filter(Installation.installer_uuid == installer_uuid)

            # Filter by status if provided
            if status:
                query = query.filter(Installation.status == status)

            # Convert start_date and end_date to datetime objects if provided
            if start_date:
                start_date = datetime.strptime(parse_date(start_date), "%Y-%m-%d")
                query = query.filter(Installation.created_at >= start_date)
            if end_date:
                end_date = datetime.strptime(parse_date(end_date), "%Y-%m-%d")
                query = query.filter(Installation.created_at <= end_date)

            # Calculate the previous date range
            if start_date and end_date:
                delta = end_date - start_date
                previous_start_date = start_date - delta
                previous_end_date = end_date - delta
            else:
                previous_start_date = previous_end_date = None

            # Count the completed, pending installation, and overdue installations

            current_completed_count = query.filter(
                Installation.status == InstallationStatus.COMPLETED
            ).count()
            current_pending_installation_count = query.filter(
                Installation.status == InstallationStatus.PENDING_INSTALLATION
            ).count()
            current_overdue_count = (
                query.join(Order)
                .filter(
                    and_(
                        Installation.status != InstallationStatus.COMPLETED,
                        Order.date_of_installation < datetime.utcnow(),
                    )
                )
                .count()
            )

            # Query the previous date range if both dates are provided
            previous_completed_count = (
                previous_pending_installation_count
            ) = previous_overdue_count = previous_total_count = 0
            if previous_start_date and previous_end_date:
                previous_query = (
                    session.query(Installation)
                    .join(Order)
                    .filter(
                        and_(
                            Installation.created_at >= previous_start_date,
                            Installation.created_at <= previous_end_date,
                        )
                    )
                )
                previous_total_count = previous_query.count()
                previous_completed_count = previous_query.filter(
                    Installation.status == InstallationStatus.COMPLETED
                ).count()
                previous_pending_installation_count = previous_query.filter(
                    Installation.status == InstallationStatus.PENDING_INSTALLATION
                ).count()
                previous_overdue_count = previous_query.filter(
                    and_(
                        Installation.status != InstallationStatus.COMPLETED,
                        Order.date_of_installation < datetime.utcnow(),
                    )
                ).count()

            # Get total number of records for pagination metadata
            total_records = query.count()
            total_pages = (total_records + per_page - 1) // per_page

            # Apply pagination
            paginated_query = query.limit(per_page).offset((page - 1) * per_page)
            installations = paginated_query.all()

            # Prepare results
            return {
                "data": installations,
                "current_page": page,
                "page_size": per_page,
                "total_records": total_records,
                "total_pages": total_pages,
                "summary": {
                    "total_installations": total_records,
                    "completed_installations": current_completed_count,
                    "pending_installations": current_pending_installation_count,
                    "overdue_installations": current_overdue_count,
                    "previous_summary": {
                        "total": previous_total_count ,
                        "completed": previous_completed_count,
                        "pending": previous_pending_installation_count,
                        "overdue": previous_overdue_count,
                    },
                    "percentage_change": {
                        "total": calculate_percentage_change(
                            total_records, previous_total_count
                        ),
                        "completed": calculate_percentage_change(
                            current_completed_count, previous_completed_count
                        ),
                        "pending": calculate_percentage_change(
                            current_pending_installation_count,
                            previous_pending_installation_count,
                        ),
                        "overdue": calculate_percentage_change(
                            current_overdue_count, previous_overdue_count
                        ),
                    },
                },
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
