from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentActiveUserDependency
from app.core.dependencies import FindQueryParameters
from app.core.dependencies import UserSkillServiceDependency
from app.schemas.user_skills_schema import InsertUserSkillAssociation
from app.schemas.user_skills_schema import PublicUserSkillAssociation

router = APIRouter(prefix="/user-skill", tags=["user-skills"])


@router.get("/")
async def read_all_user_skill_associations(find_query: FindQueryParameters, service: UserSkillServiceDependency):
    pass


@router.get("/user/{user_id}/skill/{skill_id}")
async def get_user_skill(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass


@router.post("/", response_model=PublicUserSkillAssociation)
async def create_user_skills(
    user_skill_association: InsertUserSkillAssociation,
    service: UserSkillServiceDependency,
    current_user: CurrentActiveUserDependency,
):
    return await service.add(user_skill_association)


@router.put("/user/{user_id}/skill/{skill_id}")
async def update_user_skills(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass


@router.delete("/user/{user_id}/skill/{skill_id}")
async def delete_user_skills(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass
