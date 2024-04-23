from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDependency
from app.core.dependencies import UserServiceDependency
from app.schemas.base_schema import FindBase
from app.schemas.base_schema import Message
from app.schemas.base_schema import SearchOptions
from app.schemas.user_schema import BaseUserWithPassword
from app.schemas.user_schema import FindUserResult
from app.schemas.user_schema import UpsertUser
from app.schemas.user_schema import User


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=FindUserResult)
async def get_user_list(service: UserServiceDependency, offset: int = 0, limit: int = 100):
    users = await service.get_list(FindBase(offset=offset, limit=limit))
    print(users)
    return FindUserResult(
        founds=users, search_options=SearchOptions(offset=offset, limit=limit, total_count=len(users))
    )


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: UUID, service: UserServiceDependency):
    return await service.get_by_id(user_id)


@router.post("/", status_code=201, response_model=User)
async def create_user(user: BaseUserWithPassword, service: UserServiceDependency):
    return await service.add(user)


### adicionar validacao para quano o a request tiver parametros iguais ao do current_user
@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID, user: UpsertUser, service: UserServiceDependency, current_user: CurrentUserDependency
):
    return await service.patch(id=user_id, schema=user, current_user=current_user)


# @router.patch("/change_password/{user_id}")
# async def change_password(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
#     return await service.patch_attr(id=user_id, attr="password")


@router.delete("/disable/{user_id}", response_model=Message)
async def disable_user(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
    await service.patch_attr(id=user_id, attr="is_active", value=False)
    return Message(detail="User has been desabled successfully")


@router.delete("/{user_id}", response_model=Message)
async def delete_user(user_id: UUID, service: UserServiceDependency, current_user: CurrentUserDependency):
    await service.remove_by_id(user_id, current_user=current_user)
    return Message(detail="User has been deleted successfully")


# @router.patch("/{user_id}", response_model=User)
# async def change_user_password(user_id: UUID, password: str, roservice: UserServiceDependency, current_user: CurrentUserDependency):
#     pass
# 3fa85f64-5717-4562-b3fc-2c963f66afa6
