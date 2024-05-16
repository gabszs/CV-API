from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass

from app.core.settings import settings


class Message(BaseModel):
    detail: str


class AllOptional(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)


class ModelBaseInfo(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class FindBase(BaseModel):
    ordering: Optional[str] = settings.ORDERING
    page: Optional[int] = settings.PAGE
    page_size: Optional[Union[int, str]] = settings.PAGE_SIZE


class SearchOptions(FindBase):
    total_count: Optional[int]


class FindResult(BaseModel):
    founds: Optional[List]
    search_options: Optional[SearchOptions]


class FindDateRange(BaseModel):
    created_at__lt: str
    created_at__lte: str
    created_at__gt: str
    created_at__gte: str


class FindModelResult(BaseModel):
    founds: List[Any]
    search_options: SearchOptions


class Blank(BaseModel):
    pass
