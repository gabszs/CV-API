from app.core.security import get_password_hash
from app.repository.user_repository import UserRepository
from app.schemas.user_schema import BaseUserWithPassword
from app.services.base_service import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    async def add(self, user_schema: BaseUserWithPassword):
        user_schema.password = get_password_hash(user_schema.password)
        created_user = await self._repository.create(user_schema)
        delattr(created_user, "password")
        return created_user
