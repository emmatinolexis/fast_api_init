from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.device import Device
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import AccountType


class DeviceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Device)

    def get_devices_by_user_uuid(self, user_uuid):
        with self.session_factory() as session:
            user = session.query(User).filter(User.uuid == user_uuid).first()

            if not user:
                raise Exception("User not found")

            if user.account_type == AccountType.INDIVIDUAL:
                devices = (
                    session.query(self.model)
                    .filter(self.model.user_uuid == user.uuid)
                    .all()
                )

            if user.account_type == AccountType.BUSINESS:
                devices = (
                    session.query(self.model)
                    .filter(
                        self.model.business_profile_uuid == user.business_profile_uuid
                    )
                    .all()
                )

            return devices
