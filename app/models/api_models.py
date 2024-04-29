from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base_model import Base
from sqlalchemy import Table, Column, ForeignKey, Integer, CheckConstraint
from uuid import UUID
from app.models.models_enums import SkillLevel

association_table = Table(
    "user_skill_association",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id")),
    Column("skills_id", Integer, ForeignKey("skills.id")),
    Column("skill_level", SkillLevel),
    Column("skill_years_experience", Integer, CheckConstraint("skill_years_experience >= 0 AND skill_years_experience < 70"))
)

class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="True")
    is_superuser: Mapped[bool] = mapped_column(default=False, server_default="False")

    def __init__(
        self,
        username: str,
        password: str,
        email: EmailStr,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ):
        self.username = username
        self.password = password
        self.email = email
        self.is_active = is_active
        self.is_superuser = is_superuser

class Skills(Base):
    __tablename__ = "skills"
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category: Mapped[str]

