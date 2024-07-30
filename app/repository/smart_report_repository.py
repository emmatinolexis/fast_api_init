from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.model.asset import Asset

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
            offset = (page - 1) * page_size
            base_query = self._build_base_query(session, user_uuid, business_uuid)

            total_assets = base_query.count()
            total_pages = (total_assets + page_size - 1) // page_size

            paginated_query = (
                base_query.order_by(asc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .all()
            )

            return {
                "reports": paginated_query,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def _build_base_query(
        self, session, user_uuid: str = None, business_uuid: str = None
    ):
        base_query = session.query(self.model)

        if user_uuid:
            base_query = base_query.filter(self.model.user_uuid == user_uuid)

        if business_uuid:
            base_query = base_query.filter(
                self.model.business_profile_uuid == business_uuid
            )

        return base_query

    def generate_smart_reports(
        self,
        date_from: str,
        date_to: str,
        asset_type_uuid: str,
        asset_uuids: list,
        report_types: list,
    ):
        try:
            with self.session_factory() as session:
                assets = []
                for asset_uuid in asset_uuids:
                    asset = (
                        session.query(Asset).filter(Asset.uuid == asset_uuid).first()
                    )
                    assets.append(asset)

                return assets
        except Exception as e:
            raise e
