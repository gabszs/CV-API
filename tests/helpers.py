from datetime import datetime
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.core.settings import settings
from app.models import Skill
from app.models import User
from app.models import UserSkillsAssociation
from app.models.models_enums import UserRoles
from app.schemas.base_schema import SearchOptions
from app.schemas.user_skills_schema import FindSkillsByUser
from app.schemas.user_skills_schema import PublicUserSkillAssociation
from tests.factories import create_factory_users
from tests.factories import SkillFactory
from tests.factories import UserSkillFactory
from tests.schemas import TestSkillSchema
from tests.schemas import UserModelSetup
from tests.schemas import UserSchemaWithHashedPassword
from tests.schemas import UserSkillTest


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
    get_model: bool = False,
) -> List[Union[UserSchemaWithHashedPassword, User]]:
    return_users: List[Union[UserSchemaWithHashedPassword, User]] = []
    users = create_factory_users(users_qty=users_qty, user_role=user_role, is_active=is_active)
    password_list = [factory_model.password for factory_model in users]
    for user in users:
        user.password = get_password_hash(user.password)
    session.add_all(users)
    await session.commit()
    for count, user in enumerate(users):
        await session.refresh(user)
        if get_model:
            return_users.append(user)
            continue
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


async def setup_users_data(
    session: AsyncSession, model_args: List[UserModelSetup], **kwargs
) -> List[UserSchemaWithHashedPassword]:
    return_list: List[UserSchemaWithHashedPassword] = []
    for user_setup in model_args:
        user_list = await add_users_models(
            session, users_qty=user_setup.qty, user_role=user_setup.role, is_active=user_setup.is_active, **kwargs
        )
        return_list.append(*user_list)
    return return_list


async def token(client, session: AsyncSession, base_auth_route: str = "/v1/auth", **kwargs):
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


async def setup_skill_data(
    session, skills_qty: int = 1, index: Optional[int] = None, get_model: bool = False
) -> List[Union[TestSkillSchema, Skill]]:
    return_list: List[Union[TestSkillSchema, Skill]] = []
    skills = SkillFactory.create_batch(skills_qty)
    session.add_all(skills)
    await session.commit()
    for skill in skills:
        await session.refresh(skill)
        if get_model:
            return_list.append(skill)
            continue
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


async def setup_user_skill_data(
    session: AsyncSession,
    model_args: List[UserModelSetup],
    skills_qty: int = 1,
    index: Optional[int] = None,
    get_model: bool = False,
    **kwargs,
):
    global initial
    initial = -1

    def get_by_order(total_lenght: int = skills_qty):
        global initial
        if initial == total_lenght:
            initial = 0
            return initial
        initial += 1
        return initial

    association_list: List[Union[UserSkillsAssociation, UserSkillTest]] = []
    users = await setup_users_data(session, model_args=model_args, **kwargs)
    skills = await setup_skill_data(session, skills_qty=len(model_args))

    for count, user_scheme in enumerate(users):
        schema = UserSkillFactory()
        skill = await session.get(Skill, skills[count].id)
        user = await session.get(User, user_scheme.id)
        user_skill = UserSkillsAssociation(
            user=user,
            skill=skill,
            user_id=user.id,
            skill_id=skill.id,
            skill_level=schema.skill_level,
            skill_years_experience=schema.skill_years_experience,
        )
        session.add(user_skill)
        await session.commit()
        await session.refresh(user_skill)
        if get_model:
            association_list.append(user_skill)
            continue
        association_list.append(
            UserSkillTest(
                user_id=user_skill.user_id,
                skill_id=user_skill.skill_id,
                skill_level=user_skill.skill_level,
                skill_years_experience=user_skill.skill_years_experience,
                id=user_skill.id,
                created_at=user_skill.created_at,
                updated_at=user_skill.updated_at,
            )
        )

    if index is not None:
        return association_list[index]
    return association_list


async def add_skill_to_user(
    session: AsyncSession, user_id: UUID, skill_id: Optional[int] = None, get_model: bool = False
) -> Union[UserSkillsAssociation, UserSkillTest]:
    if skill_id is None:
        skill_id = (await setup_skill_data(session, index=0)).id
    skill = await session.get(Skill, skill_id)
    user = await session.get(User, user_id)
    schema = UserSkillFactory()
    user_skill = UserSkillsAssociation(
        user=user,
        skill=skill,
        user_id=user.id,
        skill_id=skill.id,
        skill_level=schema.skill_level,
        skill_years_experience=schema.skill_years_experience,
    )
    session.add(user_skill)
    await session.commit()
    await session.refresh(user_skill)

    if get_model:
        return user_skill
    return UserSkillTest(
        user_id=user_skill.user_id,
        skill_id=user_skill.skill_id,
        skill_level=user_skill.skill_level,
        skill_years_experience=user_skill.skill_years_experience,
        id=user_skill.id,
        created_at=user_skill.created_at,
        updated_at=user_skill.updated_at,
    )


async def read_skills_by_user_id(session: AsyncSession, user_id: UUID) -> FindSkillsByUser:
    stmt = select(User).where(User.id == user_id).options(selectinload(User.skills))
    result = await session.execute(stmt)
    user = result.scalar_one()
    skills: List[PublicUserSkillAssociation] = []
    for skill in user.skills:
        skills.append(
            PublicUserSkillAssociation(
                user_id=user_id,
                skill_id=skill.skill_id,
                skill_level=skill.skill_level,
                skill_years_experience=skill.skill_years_experience,
                id=skill.id,
                created_at=skill.created_at,
                updated_at=skill.updated_at,
            )
        )

    return FindSkillsByUser(
        user_id=user_id,
        founds=skills,
        search_options=SearchOptions(
            page=1,
            page_size="all",
            ordering="-id",
            total_count=len(user.skills),
        ),
    )
