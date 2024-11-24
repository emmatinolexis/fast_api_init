from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased

from app.model.activity_log import ActivityLog
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import ActivityLogClass


class ActivityLogRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ActivityLog)

    def all_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: Optional[str] = None,
    ):
        with self.session_factory() as session:
            query = session.query(ActivityLog).order_by(ActivityLog.created_at.desc())

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            return query.all()

    def business_activity_logs(
        self,
        business_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: Optional[str] = None,
    ):
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(
                ActivityLog.business_profile_uuid == business_id
            ).order_by(ActivityLog.created_at.desc())

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            return query.all()

    def admin_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: str = None,
    ):
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(
                ActivityLog.activity_class == ActivityLogClass.ADMIN
            ).order_by(ActivityLog.created_at.desc())

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            return query.all()

    def count_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        with self.session_factory() as session:
            query = session.query(ActivityLog)

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)

            return query.count()

    def count_business_activity_logs(
        self,
        business_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(
                ActivityLog.business_profile_uuid == business_id
            )

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)
            return query.count()

    def count_admin_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(
                ActivityLog.activity_class == ActivityLogClass.ADMIN
            )

            if search_string:
                user_aliased = aliased(User)
                query = query.join(
                    user_aliased, ActivityLog.user_uuid == user_aliased.uuid
                )
                query = query.filter(
                    user_aliased.email_address.ilike(f"%{search_string}%")
                )

            if activity_types:
                query = query.filter(ActivityLog.activity_type.in_(activity_types))

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at >= start_date_obj)

            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.created_at <= end_date_obj)

            return query.count()
