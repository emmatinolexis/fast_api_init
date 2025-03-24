import logging
from typing import Any, Callable, Dict

from sqlalchemy import String, cast, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.smart_report import SmartReport
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import SmartReportStatus


class SmartReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, SmartReport)

    async def read_all_reports(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        query_parameter: str = None,
        created_by: str = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            # Initialize the query and apply filters
            query = select(self.model)

            if user_uuid:
                query = query.filter(self.model.user_uuid == user_uuid)
            if business_uuid:
                query = query.filter(self.model.business_profile_uuid == business_uuid)
            if query_parameter:
                # Add filters for both title and status using the query parameter
                query = query.filter(
                    or_(
                        self.model.title.ilike(f"%{query_parameter}%"),
                        cast(self.model.status, String).ilike(f"%{query_parameter}%"),
                    )
                )
            if created_by:
                # Filter by the creator's user UUID
                query = query.filter(self.model.user_uuid == created_by)

            # Get the total count of reports based on filters
            total_reports = await session.scalar(
                select(func.count()).select_from(query.subquery())
            )

            # Calculate total pages
            total_pages = (total_reports + page_size - 1) // page_size

            # Calculate offset for pagination
            offset = (page - 1) * page_size

            # Fetch paginated results with ordering and eager loading of relationships
            results = await session.execute(
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.user))  # Eager load user relationship
            )

            reports = results.unique().scalars().all()

            # Process the results into a list of dictionaries
            smart_reports = [
                {
                    "uuid": report.uuid,
                    "title": report.title,
                    "start_date": report.start_date,
                    "end_date": report.end_date,
                    "report_types": report.report_types,
                    "status": report.status,
                    "created_at": report.created_at,
                    "result_url": report.result_url,
                    "created_by": f"{report.user.first_name} {report.user.last_name}",
                }
                for report in reports
            ]

            # Return paginated data
            return {
                "reports": smart_reports,
                "total_reports": total_reports,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def get_unprocessed_report(self):
        try:
            async with self.session_factory() as session:
                logging.info("Generating smart report")

                result = await session.execute(
                    select(self.model)
                    .filter(self.model.status == SmartReportStatus.PENDING)
                    .options(
                        joinedload(self.model.user).joinedload(User.business_profile)
                    )
                    .order_by(desc(self.model.created_at))
                    .limit(1)
                )

                report = result.scalars().first()

                if not report:
                    return []

                return {
                    "uuid": report.uuid,
                    "title": report.title,
                    "start_date": report.start_date,
                    "end_date": report.end_date,
                    "report_types": report.report_types,
                    "status": report.status,
                    "result_url": report.result_url,
                    "asset_type_uuid": report.asset_type_uuid,
                    "asset_group_uuids": report.asset_group_uuids,
                    "created_at": report.created_at,
                    "business_name": (
                        report.user.business_profile.business_name
                        if report.user.business_profile
                        else None
                    ),
                    "user_uuid": report.user_uuid,
                    "business_profile_uuid": report.business_profile_uuid,
                    "created_by": f"{report.user.first_name} {report.user.last_name}",
                    "created_by_email": report.user.email_address,
                }

        except Exception as e:
            logging.error(f"Error generating smart report: {e}")
            raise e

    async def update_smart_report_status(
        self, smart_uuid, status: SmartReportStatus, url: str = None
    ):
        try:
            async with self.session_factory() as session:
                result = await session.execute(
                    select(self.model)
                    .filter(self.model.uuid == smart_uuid)
                    .options(
                        joinedload(self.model.user).joinedload(User.business_profile)
                    )
                )
                report = result.unique().scalars().first()
                report.status = status

                if url:
                    report.result_url = url

                await session.commit()
                await session.refresh(report)

                report_data = {
                    "uuid": report.uuid,
                    "title": report.title,
                    "start_date": report.start_date,
                    "end_date": report.end_date,
                    "report_types": report.report_types,
                    "status": report.status,
                    "result_url": report.result_url,
                    "asset_type_uuid": report.asset_type_uuid,
                    "asset_group_uuids": report.asset_group_uuids,
                    "created_at": report.created_at,
                    "business_name": report.user.business_profile.business_name,
                    "user_uuid": report.user_uuid,
                    "business_profile_uuid": report.business_profile_uuid,
                    "created_by": f"{report.user.first_name} {report.user.last_name}",
                }

                return report_data

        except Exception as e:
            raise e
