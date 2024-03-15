from sqlalchemy.orm import Mapped

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]

    # resumes: Mapped[list["Resume"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )
