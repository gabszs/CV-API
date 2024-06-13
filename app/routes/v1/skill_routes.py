from fastapi import APIRouter

from app.core.dependencies import CurrentUserDependency
from app.core.dependencies import FindQueryParameters
from app.core.dependencies import SkillServiceDependency
from app.core.security import authorize
from app.models.models_enums import CategoryOptions
from app.models.models_enums import UserRoles
from app.schemas.skill_schema import BaseSkill
from app.schemas.skill_schema import FindSkillResult
from app.schemas.skill_schema import PublicSkill
from app.schemas.skill_schema import UpdateSkill

router = APIRouter(prefix="/skill", tags=["skills"])


@router.get("/", response_model=FindSkillResult)
async def get_all_skills(find_query: FindQueryParameters, service: SkillServiceDependency):
    from icecream import ic
    ic(find_query)
    return await service.get_list(find_query)


@router.get("/{skill_id}", response_model=PublicSkill)
async def get_skill_by_id(skill_id: int, service: SkillServiceDependency):
    return await service.get_by_id(skill_id)


@router.post("/", status_code=201, response_model=PublicSkill)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR, UserRoles.BASE_USER])
async def create_skill(skill: BaseSkill, service: SkillServiceDependency, current_user: CurrentUserDependency):
    return await service.add(skill)


@router.put("/{skill_id}", response_model=PublicSkill)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR])
async def update_skill(
    skill_id: int, skill: UpdateSkill, service: SkillServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch(id=skill_id, schema=skill)


@router.patch("/{skill_id}/category/{category}", response_model=PublicSkill)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR])
async def change_skill_category(
    skill_id: int, category: CategoryOptions, service: SkillServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch_attr(id=skill_id, attr="category", value=category)


@router.patch("/{skill_id}/skill_name/{skill_name}", response_model=PublicSkill)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR])
async def change_skill_skill_name(
    skill_id: int, skill_name: str, service: SkillServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch_attr(id=skill_id, attr="skill_name", value=skill_name)


@router.delete("/{skill_id}", status_code=204)
@authorize(role=[UserRoles.ADMIN, UserRoles.MODERATOR])
async def delete_skill(skill_id: int, service: SkillServiceDependency, current_user: CurrentUserDependency):
    return await service.remove_by_id(id=skill_id)
