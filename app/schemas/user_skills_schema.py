from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.models.models_enums import SkillLevel
from app.schemas.base_schema import FindModelResult


class BaseUserSkillsAssociation(BaseModel):
    users_id: UUID
    skill_id: int
    skill_level: SkillLevel
    skill_years_experience: int


class FindUserSkillResults(FindModelResult):
    founds: List[BaseUserSkillsAssociation]