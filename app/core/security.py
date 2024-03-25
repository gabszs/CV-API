from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Tuple

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.exceptions import AuthError
from app.core.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = Settings()


def create_access_token(subject: Dict[str, str], expires_delta: timedelta = timedelta(minutes=30)) -> Tuple[str, str]:
    expire = (
        datetime.now() + expires_delta
        if expires_delta
        else datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {"exp": expire, **subject}
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    expiration_datetime = expire.strftime(settings.DATETIME_FORMAT)
    return encoded_jwt, expiration_datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decote_jwt(token: str) -> str:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return decoded_token if decoded_token["exp"] >= int(round(datetime.now().timestamp())) else None
    except Exception:
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            if not credentials.model_json_schema == "Bearer":
                raise AuthError(detail="Invalid authentication scheme")
            if not self.verify_jwt(credentials.credentials):
                raise AuthError(detail="Invalid token or expired token")
            return credentials.credentials
        else:
            raise AuthError(detail="Invaldi authorization code")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decote_jwt(jwt_token)
        except Exception as _:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid
