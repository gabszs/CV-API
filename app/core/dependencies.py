from typing import Annotated

from fastapi import Depends
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.core.exceptions import AuthError
from app.core.security import JWTBearer
from app.core.settings import settings
from app.models import User
from app.repository.user_repository import UserRepository
from app.schemas.auth_schema import Payload
from app.services.user_service import UserService


async def get_user_service(session: Session = Depends(get_session)):
    user_repository = UserRepository(session_factory=session)
    return UserService(user_repository)


async def get_current_user(token: str = Depends(JWTBearer()), service: UserService = Depends(get_user_service)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        token_data = Payload(**payload)
    except (jwt.JWTError, ValidationError):
        raise AuthError(detail="Could not validate credentials")
    current_user: User = service.get_by_id(token_data.id)
    if not current_user:
        raise AuthError(detail="User not found")
    return current_user


SessionDependency = Annotated[Session, Depends(get_session)]
UserServiceDependency = Annotated[UserService, Depends(get_current_user)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
