from typing import Callable

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundError
from app.core.settings import settings
from app.model.equipment_type import EquipmentType
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[..., AsyncSession],
        model,
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    async def read_by_options(self, schema, eager=False):
        async with self.session_factory() as session:
            schema_as_dict = schema.dict(exclude_none=True)
            ordering = schema_as_dict.get("ordering", settings.ORDERING)
            order_query = (
                getattr(self.model, ordering[1:]).desc()
                if ordering.startswith("-")
                else getattr(self.model, ordering).asc()
            )
            page = schema_as_dict.get("page", settings.PAGE)
            page_size = schema_as_dict.get("page_size", settings.PAGE_SIZE)
            filter_options = dict_to_sqlalchemy_filter_options(
                self.model, schema.dict(exclude_none=True)
            )
            query = select(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            filtered_query = query.filter(filter_options)
            query = filtered_query.order_by(order_query)
            if page_size == "all":
                result = await session.execute(query)
                query = result.unique().scalars().all()
            else:
                result = await session.execute(
                    query.limit(page_size).offset((page - 1) * page_size)
                )
                query = result.unique().scalars().all()
            total_count = await session.scalar(filtered_query.count())
            return {
                "founds": query,
                "search_options": {
                    "page": page,
                    "page_size": page_size,
                    "ordering": ordering,
                    "total_count": total_count,
                },
            }

    async def read_all(self, eager=False):
        async with self.session_factory() as session:
            query = select(self.model)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            result = await session.execute(query)
            return result.unique().scalars().all()

    async def read_all_by_uuid(self, uuid: str, eager=False):
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.asset_type_uuid == uuid)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            result = await session.execute(query)
            return result.unique().scalars().all()

    async def get_equipment_by_uuid(self, equipment_uuid: str, eager=False):
        async with self.session_factory() as session:
            query = select(EquipmentType).filter(
                EquipmentType.equipment_uuid == equipment_uuid
            )
            if eager:
                for eager in getattr(EquipmentType, "eagers", []):
                    query = query.options(joinedload(getattr(EquipmentType, eager)))
            result = await session.execute(query)
            query = result.unique().scalars().first()
            if not query:
                return None
            return query

    async def read_by_id(self, id: int, eager=False):
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.id == id)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            result = await session.execute(query)
            query = result.unique().scalars().first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            return query

    async def read_by_uuid(self, uuid: str, eager=False):
        async with self.session_factory() as session:
            query = select(self.model).filter(self.model.uuid == uuid)
            if eager:
                for eager in getattr(self.model, "eagers", []):
                    query = query.options(joinedload(getattr(self.model, eager)))
            result = await session.execute(query)
            query = result.unique().scalars().first()
            if not query:
                return None
            return query

    async def create(self, schema):
        async with self.session_factory() as session:
            query = self.model(**schema.dict())
            try:
                session.add(query)
                await session.commit()
                await session.refresh(query)
            except IntegrityError as e:
                raise e
            except Exception as e:
                raise e
            return query

    async def update(self, id: int, schema):
        async with self.session_factory() as session:
            await session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(schema.dict(exclude_none=True))
            )
            await session.commit()
            return await self.read_by_id(id)

    async def update_by_uuid(self, uuid: str, schema):
        async with self.session_factory() as session:
            await session.execute(
                update(self.model)
                .where(self.model.uuid == uuid)
                .values(schema.dict(exclude_none=True))
            )
            await session.commit()
            return await self.read_by_uuid(uuid)

    async def update_attr(self, id: int, column: str, value):
        async with self.session_factory() as session:
            await session.execute(
                update(self.model).where(self.model.id == id).values({column: value})
            )
            await session.commit()
            return await self.read_by_id(id)

    async def update_attr_by_uuid(self, uuid: str, column: str, value):
        async with self.session_factory() as session:
            await session.execute(
                update(self.model)
                .where(self.model.uuid == uuid)
                .values({column: value})
            )
            await session.commit()
            return await self.read_by_uuid(uuid)

    async def whole_update(self, id: int, schema):
        async with self.session_factory() as session:
            await session.execute(
                update(self.model).where(self.model.id == id).values(schema.dict())
            )
            await session.commit()
            return await self.read_by_id(id)

    async def delete_by_id(self, id: int):
        async with self.session_factory() as session:
            query = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            query = query.scalars().first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            await session.delete(query)
            await session.commit()

    async def delete_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            query = await session.execute(
                select(self.model).filter(self.model.uuid == uuid)
            )
            query = query.scalars().first()
            if not query:
                raise NotFoundError(detail=f"not found uuid : {uuid}")
            await session.delete(query)
            await session.commit()
