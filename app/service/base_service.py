from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError


class BaseService:
    def __init__(self, repository) -> None:
        self._repository = repository

    async def get_list(self):
        return await self._repository.read_all()

    async def get_list_by_uuid(self, uuid: str):
        return await self._repository.read_all_by_uuid(uuid)

    async def get_by_id(self, id: int):
        try:
            return await self._repository.read_by_id(id)
        except Exception as e:
            raise e

    async def get_by_uuid(self, uuid: str):
        try:
            return await self._repository.read_by_uuid(uuid)
        except Exception as e:
            raise e

    async def add(self, schema):
        try:
            return await self._repository.create(schema)
        except IntegrityError as e:
            raise e
        except Exception as e:
            raise e

    async def patch(self, id: int, schema):
        return await self._repository.update(id, schema)

    async def patch_by_uuid(self, uuid: str, schema):
        return await self._repository.update_by_uuid(uuid, schema)

    async def patch_attr(self, id: int, attr: str, value):
        return await self._repository.update_attr(id, attr, value)

    async def put_update(self, id: int, schema):
        return await self._repository.whole_update(id, schema)

    async def remove_by_id(self, id):
        return await self._repository.delete_by_id(id)

    async def remove_by_uuid(self, uuid: str):
        try:
            return await self._repository.delete_by_uuid(uuid)
        except NotFoundError:
            raise NotFoundError(detail=uuid)
