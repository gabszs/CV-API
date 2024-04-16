from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDependency
from app.core.dependencies import UserServiceDependency
from app.schemas.base_schema import FindBase
from app.schemas.base_schema import Message
from app.schemas.user_schema import BaseUserWithPassword
from app.schemas.user_schema import UpsertUser
from app.schemas.user_schema import User

router = APIRouter(prefix="/user", tags=["user"])


# skip: int = 0, limit: int = 100
# @router.get("", response_model=FindUserResult)
@router.get("", response_model=Message)
async def get_user_list(service: UserServiceDependency, offset: int = 0, limit: int = 100):
    query = FindBase(offset=offset, limit=limit)
    return await service.get_list(query)


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: UUID, service: UserServiceDependency):
    return await service.get_by_id(user_id)


@router.post("", status_code=201, response_model=User)
async def create_user(user: BaseUserWithPassword, service: UserServiceDependency):
    return await service.add(user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID, user: UpsertUser, service: UserServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch(id=user_id, schema=user)


@router.delete("/{user_id}", response_model=Message)
async def delete_user(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
    await service.remove_by_id(user_id)
    return Message(detail="User has been deleted successfully")


# @router.patch("/{user_id}", response_model=User)
# async def change_user_password(user_id: UUID, password: str, roservice: UserServiceDependency, current_user: CurrentUserDependency):
#     pass
# 3fa85f64-5717-4562-b3fc-2c963f66afa6
