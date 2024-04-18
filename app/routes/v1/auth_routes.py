from fastapi import APIRouter

from app.core.dependencies import AuthServiceDependency
from app.core.dependencies import CurrentUserDependency
from app.schemas.auth_schema import SignIn
from app.schemas.auth_schema import SignInResponse
from app.schemas.auth_schema import SignUp
from app.schemas.user_schema import User as UserSchema
# from app.schemas.base_schema import Message

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign-in", response_model=SignInResponse)
async def sign_in(user_info: SignIn, service: AuthServiceDependency):
    return await service.sign_in(user_info)


@router.post("/sign-up", response_model=UserSchema)
async def sign_up(user_info: SignUp, service: AuthServiceDependency):
    return await service.sign_up(user_info)


@router.get("/me", response_model=UserSchema)
async def get_me(current_user: CurrentUserDependency):
    return current_user
