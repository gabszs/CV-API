from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from app.models.models_enums import SkillLevel
from app.schemas.base_schema import AttrSearchOptions
from app.schemas.base_schema import FindModelResult
from app.schemas.skill_schema import BaseSkillWithId


class BaseUserSkillsAssociation(BaseModel):
    users_id: UUID
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


class FindSkillsByUser(BaseModel):
    founds: List[BaseSkillWithId]
    search_options: AttrSearchOptions
