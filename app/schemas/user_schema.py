from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr

from app.schemas.base_schema import AllOptional
from app.schemas.base_schema import FindBase
from app.schemas.base_schema import ModelBaseInfo
from app.schemas.base_schema import SearchOptions


class BaseUser(BaseModel):
    email: EmailStr
    username: str


class BaseUserWithPassword(BaseUser):
    password: str


class User(BaseUser, ModelBaseInfo):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    is_superuser: bool
    ...


class OptionalUser(User, metaclass=AllOptional):
    ...


class FindUser(FindBase, BaseUser, metaclass=AllOptional):
    ...


class UpsertUser(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    ...


class FindUserResult(BaseModel):
    founds: List[User]
    search_options: SearchOptions


class UserWithCleanPassword(BaseUserWithPassword):
    clean_password: str
