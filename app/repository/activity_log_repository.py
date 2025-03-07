from datetime import datetime
from typing import Callable, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy import func
from app.model.activity_log import ActivityLog
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import ActivityLogClass


class ActivityLogRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, ActivityLog)

    async def all_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            query = select(ActivityLog).order_by(ActivityLog.created_at.desc())

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
            result = await session.execute(query)
            return result.scalars().all()

    async def business_activity_logs(
        self,
        business_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            query = (
                select(ActivityLog)
                .filter(ActivityLog.business_profile_uuid == business_id)
                .order_by(ActivityLog.created_at.desc())
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

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            result = await session.execute(query)
            return result.scalars().all()

    async def admin_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        activity_types: List[str] = None,
        search_string: str = None,
    ):
        async with self.session_factory() as session:
            query = (
                select(ActivityLog)
                .filter(ActivityLog.activity_class == ActivityLogClass.ADMIN)
                .order_by(ActivityLog.created_at.desc())
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

            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            result = await session.execute(query)
            return result.scalars().all()

    async def count_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        async with self.session_factory() as session:
            query = select(ActivityLog)

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

            result = await session.execute(query)
            return result.scalars().count()

    async def count_business_activity_logs(
        self,
        business_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        async with self.session_factory() as session:
            # Start with counting the records
            query = (
                select(func.count())
                .select_from(ActivityLog)
                .filter(ActivityLog.business_profile_uuid == str(business_id))
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

            result = await session.execute(query)
            return result.scalar_one()

    async def count_admin_activity_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        activity_types: List[str] = None,
        search_string: str = None,
    ) -> int:
        async with self.session_factory() as session:
            # Use select(func.count()) to count the rows efficiently
            query = (
                select(func.count())
                .select_from(ActivityLog)
                .filter(ActivityLog.activity_class == ActivityLogClass.ADMIN)
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

            result = await session.execute(query)
            return result.scalar_one()
