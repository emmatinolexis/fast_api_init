from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.other_cylinder_types_repository import OtherCylinderTypeRepository
from app.repository.user_repository import UserRepository
from app.schema.gas_cylinder_schema import CreateOtherCylinderType
from app.service.base_service import BaseService
from app.util.enums import AccountType


class OtherCylinderTypeService(BaseService):
    def __init__(
        self,
        other_cylinder_type_repository: OtherCylinderTypeRepository,
        user_repository: UserRepository,
    ):
        self.other_cylinder_type_repository = other_cylinder_type_repository
        self.user_repository = user_repository
        super().__init__(other_cylinder_type_repository)

    def create_other_gas_cylinder_type(self, user_uuid: str, payload):
        user = self.user_repository.get_user_by_uuid(user_uuid)
        if not user:
            raise NotFoundError(messages.USER_NOT_FOUND + user_uuid)

        if user.get("account_type") == AccountType.BUSINESS:
            payload = CreateOtherCylinderType(
                name=payload.name,
                image_url=payload.image_url,
                empty_weight=payload.empty_weight,
                full_weight=payload.full_weight,
                business_profile_uuid=str(user.get("business_profile").uuid),
                user_uuid=str(user.get("uuid")),
            )
        elif user.get("account_type") == AccountType.INDIVIDUAL:
            payload = CreateOtherCylinderType(
                name=payload.name,
                image_url=payload.image_url,
                empty_weight=payload.empty_weight,
                full_weight=payload.full_weight,
                user_uuid=str(user.get("uuid")),
            )

        return self.other_cylinder_type_repository.create(payload)
