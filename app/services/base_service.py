from uuid import UUID

from app.repository.base_repository import BaseRepository
from app.schemas.base_schema import FindBase


class BaseService:
    def __init__(self, repository: BaseRepository) -> None:
        self._repository = repository

    async def get_list(self, schema: FindBase):
        return await self._repository.read_by_options(schema)

    async def get_by_id(self, id: UUID):
        return await self._repository.read_by_id(id)

    async def add(self, schema):
        return await self._repository.create(schema)

    async def patch(self, id: UUID, schema):
        return await self._repository.update(id, schema)

    async def patch_attr(self, id: UUID, attr: str, value):
        return await self._repository.update_attr(id, attr, value)

    async def put_update(self, id: UUID, schema):
        return await self._repository.whole_update(id, schema)

    async def remove_by_id(self, id: UUID):
        return await self._repository.delete_by_id(id)
