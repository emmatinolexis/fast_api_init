from app.core.exceptions import NotFoundError
from app.repository.organisation_contact_repository import \
    OrganisationContactRepository
from app.repository.user_repository import UserRepository
from app.schema.onboarding_schema import OrganisationContactPayload
from app.service.base_service import BaseService


class OrganisationContactService(BaseService):
    def __init__(
        self,
        organisation_contact_repository: OrganisationContactRepository,
        user_repository: UserRepository,
    ):
        self.organisation_contact_repository = organisation_contact_repository
        self.user_repository = user_repository
        super().__init__(organisation_contact_repository)

    def create_organisation_contact(self, payload: OrganisationContactPayload):
        try:
            if self.user_repository.read_by_uuid(payload.user_uuid) is None:
                raise NotFoundError(detail=payload.user_uuid)
            contact = self.organisation_contact_repository.create(payload)
            return contact
        except Exception as e:
            raise e

    def update_organisation_contact(
        self, uuid: str, payload: OrganisationContactPayload
    ):
        try:
            if self.user_repository.read_by_uuid(payload.user_uuid) is None:
                raise NotFoundError(detail=payload.user_uuid)
            contact = self.organisation_contact_repository.update_by_uuid(uuid, payload)
            return contact
        except Exception as e:
            raise e
