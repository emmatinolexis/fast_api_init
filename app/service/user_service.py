from pydantic import EmailStr

from app.core.exceptions import NotFoundError
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UpdateUserPayload, UserPayload
from app.service.base_service import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def create_user(self, payload: UserPayload):
        return self.user_repository.create_user(payload)

    def update_user_by_uuid(self, uuid: str, payload: UpdateUserPayload):
        try:
            user = self.user_repository.update_user_by_uuid(uuid, payload)
            return user if user else None
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def get_user_by_email_address(self, email: EmailStr):
        try:
            user = self.user_repository.get_user_by_email_address(email)
            return user if user else None
        except Exception as e:
            raise e
