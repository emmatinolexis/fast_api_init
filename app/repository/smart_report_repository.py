from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.model.smart_report import SmartReport
from app.repository.base_repository import BaseRepository


class SmartReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, SmartReport)

    def read_all_reports(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        with self.session_factory() as session:
            # offset = (page - 1) * page_size

            if user_uuid:
                total_reports = (
                    session.query(func.count(self.model.id))
                    .filter(self.model.user_uuid == user_uuid)
                    .scalar()
                )

                total_pages = (total_reports + page_size - 1) // page_size

                reports = (
                    session.query(self.model)
                    .filter(self.model.user_uuid == user_uuid)
                    .order_by(desc(self.model.created_at))
                    # .offset(offset)
                    # .limit(page_size)
                    .all()
                )

                return {
                    "reports": reports,
                    "total_assets": total_reports,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                }

            if business_uuid:
                total_reports = (
                    session.query(func.count(self.model.id))
                    .filter(self.model.business_profile_uuid == business_uuid)
                    .scalar()
                )

                total_pages = (total_reports + page_size - 1) // page_size

                reports = (
                    session.query(self.model)
                    .filter(self.model.business_profile_uuid == business_uuid)
                    .order_by(desc(self.model.created_at))
                    # .offset(offset)
                    # .limit(page_size)
                    .all()
                )

                # return reports

                return {
                    "reports": reports,
                    "total_assets": total_reports,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                }
