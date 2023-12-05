from app.repository.user_repository import UserRepository
from app.schema.user_schema import UpdateUser, User
from app.service.base_service import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def create_user(self, user: User):
        return self.user_repository.create_user(user)

    def update_user_by_uuid(self, uuid: str, user: UpdateUser):
        return self.user_repository.update_user_by_uuid(uuid, user)

    def get_user_by_email_address(self, email: str):
        return self.user_repository.get_user_by_email_address(email)
