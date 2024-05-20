from typing import Any
from typing import Dict
from typing import List

import factory
from factory import fuzzy
from factory.base import StubObject

from app.core.security import get_password_hash
from app.models import Skill
from app.models import User
from app.models import UserSkillsAssociation
from app.models.models_enums import CategoryOptions
from app.models.models_enums import SkillLevel
from app.schemas.user_schema import UserWithCleanPassword


def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
    stub_dict = stub.__dict__
    for key, value in stub_dict.items():
        if isinstance(value, StubObject):
            stub_dict[key] = convert_dict_from_stub(value)
    return stub_dict


def factory_object_to_dict(factory_instance):
    attributes = factory_instance.__dict__
    # Remova atributos internos que não são relevantes para o dicionário
    attributes.pop("_declarations", None)
    return attributes


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: f"user_{x}")
    email = factory.LazyAttribute(lambda x: f"{x.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}_password")
    is_active = None
    is_superuser = None


class SkillFactory(factory.Factory):
    class Meta:
        model = Skill

    skill_name = factory.Sequence(lambda x: f"skill_{x}")
    category = fuzzy.FuzzyChoice(CategoryOptions)


class UserSkillFactory(factory.Factory):
    class Meta:
        model = UserSkillsAssociation

    users_id = None
    skill_id = None
    skill_level = fuzzy.FuzzyChoice(SkillLevel)
    skill_years_experience = factory.Faker("pyint", min_value=0, max_value=1000)
    skill = None
    user = None


def create_factory_users(users_qty: int, **kwargs) -> Dict[UserFactory, str]:
    users_dict: Dict[Dict[str, List[UserFactory]], Dict[str, List[str]]] = {"users": list(), "clean_users": list()}
    for _ in range(users_qty):
        user = UserFactory(**kwargs)
        clean_password = user.password
        user.password = get_password_hash(user.password)

        clean_user = UserWithCleanPassword(
            email=user.email, username=user.username, password=user.password, clean_password=clean_password
        )

        users_dict["users"].append(user)
        users_dict["clean_users"].append(clean_user)
    return users_dict


def batch_users_by_options(
    normal_users: int = 0, admin_users: int = 0, disable_users: int = 0, disable_admins: int = 0
):
    normal_users = create_factory_users(normal_users)
    admin_users = create_factory_users(admin_users, is_superuser=True)
    disable_users = create_factory_users(disable_users, is_active=False)
    disable_admins = create_factory_users(disable_admins, is_active=False, is_superuser=True)
    users = [
        user
        for user_list in [normal_users["users"], admin_users["users"], disable_users["users"], disable_admins["users"]]
        for user in user_list
    ]
    clean_users = [
        user
        for user_list in [
            normal_users["clean_users"],
            admin_users["clean_users"],
            disable_users["clean_users"],
            disable_admins["clean_users"],
        ]
        for user in user_list
    ]
    return users, clean_users
