from uuid import UUID

from app.repository.user_skill_repository import UserSkillRepository
from app.schemas.base_schema import FindBase
from app.schemas.user_skills_schema import FindSkillsByUser
from app.services.base_service import BaseService


class UserSkillService(BaseService):
    def __init__(self, user_skill_repository: UserSkillRepository) -> None:
        self.user_skill_repository = user_skill_repository
        super().__init__(user_skill_repository)

    async def get_skill_by_user(self, user_id: UUID, find_query: FindBase) -> FindSkillsByUser:
        return await self.user_skill_repository.read_skills_by_user_id(user_id, find_query)
