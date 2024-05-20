from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict

from app.models.models_enums import CategoryOptions
from app.schemas.base_schema import FindModelResult
from app.schemas.base_schema import ModelBaseInfo


class BaseSkill(BaseModel):
    skill_name: str
    category: CategoryOptions


class PublicSkill(ModelBaseInfo, BaseSkill):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UpdateSkill(BaseSkill):
    skill_name: Optional[str]
    category: Optional[CategoryOptions]


class FindSkillResult(FindModelResult):
    founds: List[PublicSkill]
