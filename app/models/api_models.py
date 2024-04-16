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

    def __init__(self, username: str, password: str, email: EmailStr):
        self.username = username
        self.password = password
        self.email = email

    # resumes: Mapped[list["Resume"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )
