from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.models_enums import UserRoles
from app.schemas.skill_schema import BaseSkill
from app.schemas.skill_schema import PublicSkill
from app.schemas.user_schema import User as UserSchema
from app.schemas.user_skills_schema import PublicUserSkillAssociation


class UserModelSetup(BaseModel):
    qty: int = 1
    is_active: bool = True
    role: UserRoles = UserRoles.BASE_USER


class UserSchemaWithHashedPassword(UserSchema):
    password: Optional[str] = None
    hashed_password: Optional[str] = None


class SkillModelSetup(BaseSkill):
    ...


class TestSkillSchema(PublicSkill):
    ...


class UserSkillTest(PublicUserSkillAssociation):
    ...


class UserSkillId(BaseModel):
    user_id: UUID
    skill_id: int
