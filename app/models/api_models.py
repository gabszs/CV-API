from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

    # resumes: Mapped[list["Resume"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )
