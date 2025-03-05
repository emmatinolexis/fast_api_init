from datetime import datetime
from typing import Callable

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.installation import Installation
from app.model.order import Order, OrderDeviceAssignment
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.schema.installation_schema import AssignInstallerPayload, InstallationPayload
from app.util.enums import CustomerRoles, InstallationStatus
from app.util.utils import calculate_percentage_change, parse_date


class InstallationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Installation)

    async def get_installers(self):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User).filter(User.user_role_uuid == CustomerRoles.INSTALLER)
            )
            return result.scalars().all()

    async def get_installation(self, installation_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
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
            )
            return result.unique().scalars().first()

    async def get_installation_by_order_uuid(self, order_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .filter(self.model.order_uuid == order_uuid)
                .options(
                    joinedload(Installation.order).joinedload(
                        Order.order_shipping_address
                    ),
                    joinedload(Installation.installer),
                )
            )
            return result.unique().scalars().first()

    async def assign_installer_to_installation(self, payload: AssignInstallerPayload):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == payload.installation_uuid)
            )
            installation = result.scalars().first()
            if installation:
                installation.installer_uuid = payload.installer_uuid
                installation.assigned_at = datetime.now()
                await session.commit()
                await session.refresh(installation)
            return installation

    async def update_installation_status(
        self, installation_uuid: str, status: InstallationStatus
    ):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(self.model.uuid == installation_uuid)
            )
            installation = result.scalars().first()
            if installation:
                installation.status = status
                installation.installed_at = datetime.now()
                await session.commit()
                await session.refresh(installation)
            return installation

    async def get_installations(
        self,
        page: int = 1,
        per_page: int = 10,
        installer_uuid: str = None,
        status: InstallationStatus = None,
        start_date: str = None,
        end_date: str = None,
    ):
        async with self.session_factory() as session:
            # Build the base query with joinedload
            base_query = select(Installation).options(
                joinedload(Installation.order)
                .joinedload(Order.order_inventories)
                .joinedload(OrderDeviceAssignment.inventory),
                joinedload(Installation.order).joinedload(Order.order_shipping_address),
                joinedload(Installation.installer),
            )

            filters = []

            # Filter by installer_uuid if provided
            if installer_uuid:
                filters.append(Installation.installer_uuid == installer_uuid)

            # Filter by status if provided
            if status:
                filters.append(Installation.status == status)

            # Convert start_date and end_date to datetime objects if provided
            if start_date:
                start_date = datetime.strptime(parse_date(start_date), "%Y-%m-%d")
                filters.append(Installation.created_at >= start_date)
            if end_date:
                end_date = datetime.strptime(parse_date(end_date), "%Y-%m-%d")
                filters.append(Installation.created_at <= end_date)

            # Apply filters to the query
            if filters:
                base_query = base_query.filter(and_(*filters))

            # Calculate the previous date range
            if start_date and end_date:
                delta = end_date - start_date
                previous_start_date = start_date - delta
                previous_end_date = end_date - delta
            else:
                previous_start_date = previous_end_date = None

            # Execute the base query to get total records
            total_records_result = await session.execute(base_query)
            total_records = len(total_records_result.unique().scalars().all())

            # Count the completed, pending, and overdue installations
            completed_query = base_query.filter(
                Installation.status == InstallationStatus.COMPLETED
            )
            pending_query = base_query.filter(
                Installation.status == InstallationStatus.PENDING_INSTALLATION
            )
            overdue_query = base_query.join(Order).filter(
                and_(
                    Installation.status != InstallationStatus.COMPLETED,
                    Order.date_of_installation < datetime.utcnow(),
                )
            )

            completed_count_result = await session.execute(completed_query)
            current_completed_count = len(completed_count_result.scalars().all())

            pending_count_result = await session.execute(pending_query)
            current_pending_installation_count = len(
                pending_count_result.unique().scalars().all()
            )

            overdue_count_result = await session.execute(overdue_query)
            current_overdue_count = len(overdue_count_result.scalars().all())

            # Query the previous date range if both dates are provided
            previous_completed_count = (
                previous_pending_installation_count
            ) = previous_overdue_count = previous_total_count = 0

            if previous_start_date and previous_end_date:
                previous_filters = [
                    Installation.created_at >= previous_start_date,
                    Installation.created_at <= previous_end_date,
                ]
                previous_query = select(Installation).filter(and_(*previous_filters))

                previous_total_result = await session.execute(previous_query)
                previous_total_count = len(previous_total_result.scalars().all())

                previous_completed_result = await session.execute(
                    previous_query.filter(
                        Installation.status == InstallationStatus.COMPLETED
                    )
                )
                previous_completed_count = len(
                    previous_completed_result.scalars().all()
                )

                previous_pending_result = await session.execute(
                    previous_query.filter(
                        Installation.status == InstallationStatus.PENDING_INSTALLATION
                    )
                )
                previous_pending_installation_count = len(
                    previous_pending_result.scalars().all()
                )

                previous_overdue_result = await session.execute(
                    previous_query.filter(
                        and_(
                            Installation.status != InstallationStatus.COMPLETED,
                            Order.date_of_installation < datetime.utcnow(),
                        )
                    )
                )
                previous_overdue_count = len(previous_overdue_result.scalars().all())

            # Calculate pagination metadata
            total_pages = (total_records + per_page - 1) // per_page
            paginated_query = base_query.limit(per_page).offset((page - 1) * per_page)

            # Execute paginated query
            paginated_result = await session.execute(paginated_query)
            installations = paginated_result.scalars().all()

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
                        "total": previous_total_count,
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

    async def create_installation(self, installation_payload: InstallationPayload):
        async with self.session_factory() as session:  # Use async session
            try:
                # Create the installation record
                installation = Installation(
                    order_uuid=installation_payload.order_uuid,
                )
                session.add(installation)

                # Fetch the related order
                order_query = await session.execute(
                    select(Order).filter_by(uuid=installation_payload.order_uuid)
                )
                order = order_query.scalars().first()

                # Update order details if found
                if order:
                    order.date_of_installation = (
                        installation_payload.date_of_installation
                    )
                    order.time_of_installation = (
                        installation_payload.time_of_installation
                    )

                # Commit transaction
                await session.commit()
                await session.refresh(installation)

                return installation
            except Exception as e:
                raise e
