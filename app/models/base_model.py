from datetime import datetime
from uuid import UUID
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import text
from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.sql import func


def generate_uuid4() -> str:
    return str(uuid4)


class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[UUID] = mapped_column(types.Uuid, primary_key=True, init=False, server_default=text("gen_random_uuid()"))
    created_at = Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
