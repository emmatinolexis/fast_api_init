from app.repository.contact_sale_repository import ContactSaleRepository
from app.service.base_service import BaseService


class ContactSaleService(BaseService):
    def __init__(self, contact_sale_repository: ContactSaleRepository):
        self.contact_sale_repository = contact_sale_repository
        super().__init__(contact_sale_repository)
