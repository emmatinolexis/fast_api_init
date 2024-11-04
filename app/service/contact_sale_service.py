from app.repository.contact_sale_repository import ContactSaleRepository
from app.model.contact_sale import ContactSale
from app.schema.contact_sale_schema import ContactSale as ContactSaleSchema


class ContactSaleService:
    def __init__(self, contact_sale_repository: ContactSaleRepository):
        self.contact_sale_repository = contact_sale_repository

    def create_contact_sale(self, payload: ContactSaleSchema):
        contact_sale = ContactSale(
            phone_number=payload.phone_number,
            call_time=payload.call_time,
            user_uuid=payload.user_uuid,
            status=payload.status,
        )
        return self.contact_sale_repository.create_contact_sale(contact_sale)
