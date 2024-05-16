from app.repository.skill_repository import SkillRepository
from app.schemas.base_schema import FindBase
from app.services.base_service import BaseService


class SkillService(BaseService):
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository
        super().__init__(skill_repository)

    async def get_list(self, schema: FindBase):
        return await self._repository.read_by_options(schema, eager=True, unique=True)
