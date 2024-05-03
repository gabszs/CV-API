from pydantic import BaseModel

from app.models.models_enums import CategoryOptions
from app.schemas.base_schema import ModelBaseInfo


class BaseSkill(BaseModel):
    skill_name: str
    category: CategoryOptions


class PublicSkill(ModelBaseInfo, BaseSkill):
    id: int
