from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.package_item import PackageItem
from app.repository.base_repository import BaseRepository


class PackageItemRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, PackageItem)
