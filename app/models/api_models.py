from typing import List
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import Base
from app.models.models_enums import SkillLevel


class UserSkillsAssociation(Base):
    __tablename__ = "user_skills_association"

    users_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)
    skill_level: Mapped[SkillLevel]
    skill_years_experience: Mapped[int]
    skill: Mapped["Skill"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="skills")


class User(Base):
    __tablename__ = "users"

    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    skills: Mapped[List["UserSkillsAssociation"]] = relationship(back_populates="user")
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


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_name: Mapped[str]
    category: Mapped[Optional[str]]
    users: Mapped[List["UserSkillsAssociation"]] = relationship(back_populates="skill")
