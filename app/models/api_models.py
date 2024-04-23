from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base_model import Base


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
        self.is_superuser

    # resumes: Mapped[list["Resume"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )
