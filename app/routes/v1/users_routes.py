from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from app.core.dependencies import CurrentUserDependency
from app.core.dependencies import UserServiceDependency
from app.core.security import JWTBearer
from app.schemas.base_schema import Message
from app.schemas.user_schema import FindUser
from app.schemas.user_schema import UpsertUser
from app.schemas.user_schema import User

router = APIRouter(prefix="/user", tags=["user"], dependencies=[Depends(JWTBearer())])


@router.get("", response_model=User)
async def get_user_list(find_query: FindUser, service: UserServiceDependency, current_user: CurrentUserDependency):
    return await service.get_list(find_query)


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
    return await service.get_by_id(user_id)


@router.post("", status_code=201, response_model=User)
async def create_user(user: UpsertUser, service: UserServiceDependency, current_user: CurrentUserDependency):
    return await service.add(user)


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID, user: UpsertUser, service: UserServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch(id=user_id, schema=user)


@router.delete("/{user_id}", response_model=Message)
async def delete_user(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
    await service.remove_by_id(user_id)
    return Message(detail="User has been deleted successfully")
