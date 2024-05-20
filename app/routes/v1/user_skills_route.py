from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import FindQueryParameters
from app.core.dependencies import UserServiceDependency

router = APIRouter(prefix="/user-skills", tags=["user-skills"])


@router.get("/")
async def read_all_user_skill_associations(find_query: FindQueryParameters, service: UserServiceDependency):
    pass


@router.get("/user/{user_id}/skill/{skill_id}")
async def get_user_skill(user_id: UUID, skill_id: int, service: UserServiceDependency):
    pass


@router.post("/")
async def create_user_skills(service: UserServiceDependency):
    pass


@router.put("/user/{user_id}/skill/{skill_id}")
async def update_user_skills(user_id: UUID, skill_id: int, service: UserServiceDependency):
    pass


@router.delete("/user/{user_id}/skill/{skill_id}")
async def delete_user_skills(user_id: UUID, skill_id: int, service: UserServiceDependency):
    pass
