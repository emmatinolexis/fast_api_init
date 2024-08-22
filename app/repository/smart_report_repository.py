import logging
from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import String, cast, desc, or_
from sqlalchemy.orm import Session, joinedload

from app.model.smart_report import SmartReport
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import SmartReportStatus


class SmartReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, SmartReport)

    def read_all_reports(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        query_parameter: str = None,
        created_by: str = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        with self.session_factory() as session:
            # Initialize the query and filters
            query = session.query(self.model)

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
                # Join with the user model to filter by creator's name
                query = query.filter(self.model.user_uuid == created_by)

            # Query to get the total count of reports based on filters
            total_reports = query.count()

            # Calculate total pages
            total_pages = (total_reports + page_size - 1) // page_size

            # Ensure page is within valid range
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages

            # Calculate offset
            offset = (page - 1) * page_size

            # Fetch paginated results with ordering and relationships loaded
            reports = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .options(joinedload(self.model.user))
                .all()
            )

            smart_reports = []
            for report in reports:
                report_data = {
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
                smart_reports.append(report_data)

            return {
                "reports": smart_reports,
                "total_assets": total_reports,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    # def read_all_reports(
    #     self,
    #     user_uuid: str = None,
    #     business_uuid: str = None,
    #     name: str = None,
    #     status: str = None,
    #     created_by: str = None,
    #     page: int = 1,
    #     page_size: int = 10,
    # ) -> Dict[str, Any]:
    #     with self.session_factory() as session:
    #         # Initialize the query and filters
    #         query = session.query(self.model)
    #         if user_uuid:
    #             query = query.filter(self.model.user_uuid == user_uuid)
    #         if business_uuid:
    #             query = query.filter(self.model.business_profile_uuid == business_uuid)
    #         if name:
    #             query = query.filter(self.model.title.ilike(f"%{name}%"))
    #         if status:
    #             query = query.filter(
    #                 self.model.status == convert_smart_report_status_user(status)
    #             )
    #         if created_by:
    #             # Join with the user model to filter by creator's name
    #             query = query.filter(self.model.user_uuid == created_by)
    #
    #         # Query to get the total count of reports based on filters
    #         total_reports = query.count()
    #
    #         # Calculate total pages
    #         total_pages = (total_reports + page_size - 1) // page_size
    #
    #         # Ensure page is within valid range
    #         if page < 1:
    #             page = 1
    #         elif page > total_pages:
    #             page = total_pages
    #
    #         # Calculate offset
    #         offset = (page - 1) * page_size
    #
    #         # Fetch paginated results with ordering and relationships loaded
    #         reports = (
    #             query.order_by(desc(self.model.created_at))
    #             .offset(offset)
    #             .limit(page_size)
    #             .options(joinedload(self.model.user))
    #             .all()
    #         )
    #
    #         smart_reports = []
    #         for report in reports:
    #             report_data = {
    #                 "uuid": report.uuid,
    #                 "title": report.title,
    #                 "start_date": report.start_date,
    #                 "end_date": report.end_date,
    #                 "report_types": report.report_types,
    #                 "status": convert_smart_report_status(report.status),
    #                 "created_at": report.created_at,
    #                 "result_url": report.result_url,
    #                 "created_by": f"{report.user.first_name} {report.user.last_name}",
    #             }
    #             smart_reports.append(report_data)
    #
    #         return {
    #             "reports": smart_reports,
    #             "total_assets": total_reports,
    #             "total_pages": total_pages,
    #             "current_page": page,
    #             "page_size": page_size,
    #         }

    def get_unprocessed_report(self):
        try:
            with self.session_factory() as session:
                logging.info("Generating smart report")
                report_data = []
                report = (
                    session.query(self.model)
                    .filter(self.model.status == SmartReportStatus.PENDING)
                    .options(
                        joinedload(self.model.user).joinedload(User.business_profile)
                    )
                    .order_by(desc(self.model.created_at))
                    .first()
                )

                if not report:
                    return report_data

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
                    "created_by_email": report.user.email_address,
                }

                return report_data

        except Exception as e:
            raise e

    def update_smart_report_status(
        self, smart_uuid, status: SmartReportStatus, url: str = None
    ):
        try:
            with self.session_factory() as session:
                report = (
                    session.query(self.model)
                    .filter(self.model.uuid == smart_uuid)
                    .options(
                        joinedload(self.model.user).joinedload(User.business_profile)
                    )
                    .first()
                )
                report.status = status

                if url:
                    report.result_url = url

                session.commit()
                session.refresh(report)

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
