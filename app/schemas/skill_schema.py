from typing import List

from pydantic import BaseModel
from pydantic import ConfigDict

from app.models.models_enums import CategoryOptions
from app.schemas.base_schema import ModelBaseInfo
from app.schemas.base_schema import SearchOptions


class BaseSkill(BaseModel):
    skill_name: str
    category: CategoryOptions


class PublicSkill(ModelBaseInfo, BaseSkill):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FindSkillResult(BaseModel):
    founds: List[PublicSkill]
    search_options: SearchOptions


# ps = PublicSkill(skill_name=Test)
# FindSkillResult()
