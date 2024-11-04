from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session
from app.model.contact_sale import ContactSale
from app.repository.base_repository import BaseRepository

class ContactSaleRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, ContactSale)

    def create_contact_sale(self, contact_sale: ContactSale):
        with self.session_factory() as session:
            session.add(contact_sale)
            session.commit()
            session.refresh(contact_sale)
            return contact_sale
