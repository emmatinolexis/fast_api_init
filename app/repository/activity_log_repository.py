from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.model.activity_log import ActivityLog
from app.repository.base_repository import BaseRepository
from app.util.enums import ActivityLogClass


class ActivityLogRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ActivityLog)

    def all_activity_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        with self.session_factory() as session:
            query = session.query(ActivityLog)
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            return query.all()

    def business_activity_logs(self, business_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(ActivityLog.business_profile_uuid==business_id)

            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            return query.all() 


    def admin_activity_logs(self,start_date: Optional[str] = None, end_date: Optional[str] = None, page: int = 1, page_size: int = 10):
        with self.session_factory() as session:
            query = session.query(ActivityLog).filter(ActivityLog.activity_class==ActivityLogClass.ADMIN)
            if start_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date >= start_date_obj)
            if end_date:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(ActivityLog.date <= end_date_obj)

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            return query.all()
        

    def count_activity_logs(self) -> int:
        with self.session_factory() as session:
            return session.query(ActivityLog).count()
        

    def count_business_activity_logs(self, business_id: str) -> int:
        with self.session_factory() as session:
            return session.query(ActivityLog).filter(ActivityLog.business_profile_uuid==business_id).count()
        

    def count_admin_activity_logs(self) -> int:
        with self.session_factory() as session:
            return session.query(ActivityLog).filter(ActivityLog.activity_class==ActivityLogClass.ADMIN).count()
