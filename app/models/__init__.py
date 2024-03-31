from uuid import UUID

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative

from .api_models import User


@as_declarative()
class BaseModel:
    id: UUID
    __name__: str

    @declared_attr
    def __table__(cls):
        return cls.__name__.lower()


__all__ = ["User", "BaseModel"]
