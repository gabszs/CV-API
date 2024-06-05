from datetime import datetime
from typing import List
from typing import Optional

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.core.settings import settings
from app.models.models_enums import UserRoles
from tests.factories import create_factory_users
from tests.factories import SkillFactory
from tests.factories import UserFactory
from tests.schemas import TestSkillSchema
from tests.schemas import UserModelSetup
from tests.schemas import UserSchemaWithHashedPassword


def validate_datetime(data_string):
    try:
        datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except ValueError:
        try:
            datetime.strptime(data_string, "%Y-%m-%dT%H:%M:%S")
            return True
        except ValueError:
            return False


async def get_skill_by_index(client, index: int = 0, token_header: Optional[str] = None):
    response = await client.get(f"{settings.base_skill_url}/?ordering=id", headers=token_header)
    return response.json()["founds"][index]


async def get_user_by_index(client, index: int = 0, token_header: Optional[str] = None):
    response = await client.get(f"{settings.base_users_url}/?ordering=username", headers=token_header)
    return response.json()["founds"][index]


async def add_users_models(
    session: AsyncSession,
    users_qty: int = 1,
    user_role: UserRoles = UserRoles.BASE_USER,
    is_active=True,
    index: Optional[int] = None,
) -> List[UserFactory]:
    return_users: List[UserFactory] = []
    users = create_factory_users(users_qty=users_qty, user_role=user_role, is_active=is_active)
    password_list = [factory_model.password for factory_model in users]
    for user in users:
        user.password = get_password_hash(user.password)
    session.add_all(users)
    await session.commit()
    for count, user in enumerate(users):
        await session.refresh(user)
        return_users.append(
            UserSchemaWithHashedPassword(
                id=user.id,
                created_at=user.created_at,
                updated_at=user.updated_at,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                role=user.role,
                password=password_list[count],
                hashed_password=user.password,
            )
        )
    if index is not None:
        return return_users[index]
    return return_users


async def setup_users_data(session, model_args: List[UserModelSetup]) -> List[UserSchemaWithHashedPassword]:
    return_list: List[UserSchemaWithHashedPassword] = []
    for user_setup in model_args:
        user_list = await add_users_models(
            session, users_qty=user_setup.qty, user_role=user_setup.role, is_active=user_setup.is_active
        )
        return_list.append(*user_list)
    return return_list


async def token(client, session, base_auth_route: str = "/v1/auth", **kwargs):
    user = await add_users_models(session=session, index=0, **kwargs)
    response = await client.post(
        f"{base_auth_route}/sign-in", json={"email__eq": user.email, "password": user.password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def get_user_token(client: AsyncClient, user: UserSchemaWithHashedPassword) -> str:
    response = await client.post(
        f"{settings.base_auth_route}/sign-in", json={"email__eq": user.email, "password": user.password}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def setup_skill_data(session, skills_qty: int = 1, index: Optional[int] = None) -> List[TestSkillSchema]:
    return_list: List[TestSkillSchema] = []
    skills = SkillFactory.create_batch(skills_qty)
    session.add_all(skills)
    await session.commit()
    for skill in skills:
        await session.refresh(skill)
        return_list.append(
            TestSkillSchema(
                id=skill.id,
                skill_name=skill.skill_name,
                category=skill.category,
                created_at=skill.created_at,
                updated_at=skill.updated_at,
            )
        )
    if index is not None:
        return return_list[index]
    return return_list


# async def get_search_normal_user_skill_data(client, session, normal_users: int = 1, skills_qty: int = 1, **kwargs):
#     await setup_users_data(session, normal_users=normal_users, **kwargs)
#     await setup_skill_data(session, skills_qty)
#     user_search = await get_user_by_index(client)
#     skill_search = await get_skill_by_index(client)
#     return user_search, skill_search
