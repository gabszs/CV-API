from datetime import timedelta
from typing import List

from app.core.exceptions import AuthError
from app.core.security import create_access_token
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.core.settings import settings
from app.models import User
from app.repository.user_repository import UserRepository
from app.schemas.auth_schema import Payload
from app.schemas.auth_schema import SignIn
from app.schemas.auth_schema import SignInResponse
from app.schemas.auth_schema import SignUp
from app.schemas.user_schema import BaseUserWithPassword
from app.services.base_service import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository) -> SignInResponse:
        self.user_repository = user_repository
        super().__init__(user_repository)

    async def sign_in(self, sign_in_info: SignIn):
        # find_user = FindUser()
        # find_user.email__eq = sign_in_info.email__eq
        # user: List[User] = await self.user_repository.read_by_options(find_user)["founds"]
        user: List[User] = await self.user_repository.read_by_email(email=sign_in_info.email__eq)
        user
        if len(user) < 1:
            raise AuthError(detail="Incorrect email or password")
        found_user = user[0]

        if not verify_password(sign_in_info.password, found_user.password):
            raise AuthError(detail="Incorrect email or password")

        delattr(found_user, "password")

        payload = Payload(id=found_user.id, email=found_user.email, username=found_user.username)

        token_lifespan = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expiration_datetime = create_access_token(payload.model_dump(), token_lifespan)
        # sign_in_result = {"access_token": access_token, "expiration": expiration_datetime, "user_info": found_user}
        sign_in_result = SignInResponse(access_token=access_token, expiration=expiration_datetime, user_info=found_user)
        return sign_in_result

    async def sign_up(self, user_info: SignUp):
        user = BaseUserWithPassword(**user_info.model_dump(exclude_none=True))
        user.password = get_password_hash(user_info.password)
        created_user = await self.user_repository.create(user)
        delattr(created_user, "password")
        return created_user
