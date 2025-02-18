from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.model.rnd_image_model import RNDImage
from app.repository.base_repository import BaseRepository


class RNDImageRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, RNDImage)

    def save_chunk(self, image_id: str, chunk_index: int, chunk_data: bytes):
        image_chunk = RNDImage(
            image_id=image_id, chunk_index=chunk_index, chunk_data=chunk_data
        )
        self.db_session.add(image_chunk)
        self.db_session.commit()

    def get_chunks(self, image_id: str):
        return (
            self.db_session.query(RNDImage)
            .filter_by(image_id=image_id)
            .order_by(RNDImage.chunk_index.asc())
            .all()
        )

    def delete_chunks(self, image_id: str):
        self.db_session.query(RNDImage).filter_by(image_id=image_id).delete()
        self.db_session.commit()
