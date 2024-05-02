from app.repository.skill_repository import SkillRepository
from app.services.base_service import BaseService


class SkillService(BaseService):
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository
        super().__init__(skill_repository)
