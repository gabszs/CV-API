from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import CurrentUserDependency
from app.core.dependencies import FindQueryParameters
from app.core.dependencies import UserSkillServiceDependency
from app.core.security import authorize
from app.models.models_enums import UserRoles
from app.schemas.base_schema import FindBase
from app.schemas.user_skills_schema import FindSkillsByUser
from app.schemas.user_skills_schema import FindUserSkillResults
from app.schemas.user_skills_schema import InsertUserSkillAssociation
from app.schemas.user_skills_schema import PublicUserSkillAssociation
from app.schemas.user_skills_schema import UpdateUserSkillAssociation

router = APIRouter(prefix="/user-skill", tags=["user-skills"])


@router.get("/", response_model=FindUserSkillResults)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR])
async def read_all_user_skill_associations(
    find_query: FindQueryParameters, service: UserSkillServiceDependency, current_user: CurrentUserDependency
):
    return await service.get_list(find_query, unique=True)


@router.get("/{user_skill_id}", response_model=PublicUserSkillAssociation)
@authorize(role=[UserRoles.MODERATOR, UserRoles.ADMIN], allow_same_id=True)
async def get_user_by_id(user_skill_id: UUID, service: UserSkillServiceDependency, current_user: CurrentUserDependency):
    return await service.get_by_id(user_skill_id, not_unique_pk=True)


# @router.get("/user/{user_id}/skill/{skill_id}")
# async def get_users_skills(user_id: UUID, skill_id: int, service: UserSkillServiceDependency):
#     pass


@router.post("/", status_code=201, response_model=PublicUserSkillAssociation)
async def create_user_skills(
    user_skill_association: InsertUserSkillAssociation,
    service: UserSkillServiceDependency,
    current_user: CurrentUserDependency,
):
    return await service.add(user_skill_association)


# test
@router.get("/skills-by-user/{user_id}", response_model=FindSkillsByUser)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR], allow_same_id=True)
async def get_skills_by_user(
    user_id: UUID,
    service: UserSkillServiceDependency,
    current_user: CurrentUserDependency,
    find_query: FindBase = Depends(),
):
    return await service.get_skill_by_user(user_id, find_query)


@router.put("/{user_skill_id}", response_model=PublicUserSkillAssociation)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR], allow_same_id=True)
async def update_user_skills(
    user_skill_id: UUID,
    user_skill: UpdateUserSkillAssociation,
    service: UserSkillServiceDependency,
    current_user: CurrentUserDependency,
):
    return await service.patch(user_skill_id, schema=user_skill, not_unique_pk=True)


@router.delete("/{user_skill_id}", status_code=204)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR], allow_same_id=True)
async def delete_user_skills(
    user_skill_id: UUID, service: UserSkillServiceDependency, current_user: CurrentUserDependency
):
    await service.remove_by_id(id=user_skill_id, not_unique_pk=True)
