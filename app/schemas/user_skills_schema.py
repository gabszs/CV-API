from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from app.models.models_enums import SkillLevel
from app.schemas.base_schema import FindModelResult


class BaseUserSkillsAssociation(BaseModel):
    user_id: UUID
    skill_id: int
    skill_level: SkillLevel
    skill_years_experience: int = Field(ge=-1, le=70)


class InsertUserSkillAssociation(BaseUserSkillsAssociation):
    ...


class PublicUserSkillAssociation(BaseUserSkillsAssociation):
    id: UUID
    created_at: datetime
    updated_at: datetime


class FindUserSkillResults(FindModelResult):
    founds: List[BaseUserSkillsAssociation]


class FindSkillsByUser(FindModelResult):
    user_id: UUID
    founds: List[PublicUserSkillAssociation]
