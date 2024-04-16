from typing import List
from typing import Optional

from pydantic import BaseModel
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


class User(ModelBaseInfo, BaseUser, metaclass=AllOptional):
    ...


class FindUser(FindBase, BaseUser, metaclass=AllOptional):
    ...


class UpsertUser(BaseUser, metaclass=AllOptional):
    ...


class FindUserResult(BaseModel):
    founds: Optional[List[User]]
    search_options: Optional[SearchOptions]
