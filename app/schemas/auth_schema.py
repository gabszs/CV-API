from datetime import datetime

from pydantic import BaseModel

from app.schemas.user_schema import User


class SignIn(BaseModel):
    email__eq: str
    password: str


class SignUp(BaseModel):
    email: str
    password: str
    username: str


class Payload(BaseModel):
    id: int
    email: str
    username: str


class SignInResponse(BaseModel):
    access_token: str
    expiration: datetime
    user_info: User
