from app.repository.user_skill_repository import UserSkillRepository
from app.services.base_service import BaseService


class UserSkillService(BaseService):
    def __init__(self, user_skill_repository: UserSkillRepository):
        self.user_skill_repository = user_skill_repository
        super().__init__(user_skill_repository)
