from typing import Any
from typing import Dict

import factory
from factory import fuzzy
from factory.base import StubObject

from app.models import Skill
from app.models import User
from app.models import UserSkillsAssociation
from app.models.models_enums import CategoryOptions
from app.models.models_enums import SkillLevel
from app.models.models_enums import UserRoles


def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
    stub_dict = stub.__dict__
    for key, value in stub_dict.items():
        if isinstance(value, StubObject):
            stub_dict[key] = convert_dict_from_stub(value)
    return stub_dict


def factory_object_to_dict(factory_instance):
    attributes = factory_instance.__dict__
    attributes.pop("_declarations", None)
    return attributes


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: f"user_{x}")
    email = factory.LazyAttribute(lambda x: f"{x.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}_password")
    role = UserRoles.BASE_USER
    is_active = None


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
    skill_years_experience = factory.Faker("pyint", min_value=0, max_value=70)
    skill = None
    user = None


def create_factory_users(users_qty: int = 1, user_role: UserRoles = UserRoles.BASE_USER, is_active=True):
    return UserFactory.create_batch(users_qty, role=user_role, is_active=is_active)
