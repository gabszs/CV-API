from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import UserSkillServiceDependency
from app.schemas.base_schema import FindBase
from app.schemas.user_skills_schema import FindSkillsByUser
from app.schemas.user_skills_schema import InsertUserSkillAssociation
from app.schemas.user_skills_schema import PublicUserSkillAssociation

router = APIRouter(prefix="/user-skill", tags=["user-skills"])


# @router.get("/")
# async def read_all_user_skill_associations(find_query: a, service: UserSkillServiceDependency):
#     pass


@router.get("/user/{user_id}/skill/{skill_id}")
async def get_user_skill(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass


@router.post("/", status_code=201, response_model=PublicUserSkillAssociation)
async def create_user_skills(
    user_skill_association: InsertUserSkillAssociation,
    service: UserSkillServiceDependency,
    # current_user: CurrentActiveUserDependency,
):
    return await service.add(user_skill_association)


@router.get("/get-skills-by-user/{user_id}", response_model=FindSkillsByUser)
async def get_skills_by_user(
    user_id: UUID,
    service: UserSkillServiceDependency,
    find_query: FindBase = Depends(),
    # current_user: CurrentActiveUserDependency,
):
    return await service.get_skill_by_user(user_id, find_query)


@router.put("/user/{user_id}/skill/{skill_id}")
async def update_user_skills(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass


@router.delete("/user/{user_id}/skill/{skill_id}")
async def delete_user_skills(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
    pass
