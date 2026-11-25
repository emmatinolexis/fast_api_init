from datetime import datetime, timedelta
from typing import Callable, Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.logger import get_logger
from app.model.business_profile import BusinessProfile
from app.model.user import User

from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus
from app.util.utils import parse_date


class BusinessProfileRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, BusinessProfile)

    def _parse_dates(self, start_date, end_date):
        """Helper function to parse dates safely."""
        try:
            start_date_obj = parse_date(start_date) if start_date else None
            end_date_obj = parse_date(end_date) if end_date else None
        except ValueError as e:
            raise e
        return start_date_obj, end_date_obj
