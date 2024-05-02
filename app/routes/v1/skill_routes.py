from fastapi import APIRouter

from app.core.dependencies import SkillServiceDependency
from app.schemas.base_schema import Message
from app.schemas.skill_schema import Skill

router = APIRouter(prefix="/skill", tags=["skills"])
# from app.schemas.base_schema import SearchOptions


@router.get("/")
async def get_all_skills(offset: int = 0, limit: int = 100):
    pass


@router.get("/{skill_id}")
async def get_skill_by_id(skill_id: int):
    pass


@router.post("/", status_code=201)
async def create_skill(skill: Skill, service: SkillServiceDependency):
    # return skill
    return await service.add(Skill)


@router.put("/{skill_id}")
async def update_skill(skill_id: int):
    pass


@router.patch("/change_category/{skill_id}")
async def change_skill_category(skill_id: int):
    pass


@router.patch("/change_skill_name/{skill_id}")
async def change_skill_skill_name(skill_id: int):
    pass


@router.delete("/{skill_id}", response_model=Message)
async def delete_skill(skill_id: int):
    return Message(detail="Skill has been deleted successfully")
