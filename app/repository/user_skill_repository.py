from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.models import UserSkillsAssociation
from app.repository.base_repository import BaseRepository


class UserSkillRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSkillsAssociation)
