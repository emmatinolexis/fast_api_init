from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.contact_sale import ContactSale
from app.repository.base_repository import BaseRepository


class ContactSaleRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, ContactSale)

    async def create_contact_sale(self, contact_sale: ContactSale) -> ContactSale:
        async with self.session_factory() as session:
            try:
                session.add(contact_sale)
                await session.commit()
                await session.refresh(contact_sale)
                return contact_sale
            except Exception as e:
                await session.rollback()
                raise e
