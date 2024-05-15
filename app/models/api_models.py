from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import Base
from app.models.models_enums import CategoryOptions
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
    skills: Mapped[List["UserSkillsAssociation"]] = relationship(back_populates="user", init=False)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="True")
    is_superuser: Mapped[bool] = mapped_column(default=False, server_default="False")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    skill_name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[CategoryOptions]
    users: Mapped[List["UserSkillsAssociation"]] = relationship(back_populates="skill", init=False)
