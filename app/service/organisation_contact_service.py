from app.core.exceptions import NotFoundError
from app.repository.organisation_contact_repository import OrganisationContactRepository
from app.repository.user_repository import UserRepository
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

    def create_organisation_contact(self, organisation_contact):
        if self.user_repository.read_by_uuid(organisation_contact.user_uuid) is None:
            raise NotFoundError(detail="User Not Found")
        return self.organisation_contact_repository.create(organisation_contact)
