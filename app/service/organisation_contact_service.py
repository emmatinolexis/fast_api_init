from app.repository.organisation_contact_repository import OrganisationContactRepository
from app.service.base_service import BaseService


class OrganisationContactService(BaseService):
    def __init__(self, organisation_contact_repository: OrganisationContactRepository):
        self.organisation_contact_repository = organisation_contact_repository
        super().__init__(organisation_contact_repository)
