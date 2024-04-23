from typing import Dict
from typing import List

import factory

from app.core.security import get_password_hash
from app.models import User


def factory_object_to_dict(factory_instance):
    attributes = factory_instance.__dict__
    # Remova atributos internos que não são relevantes para o dicionário
    attributes.pop("_declarations", None)
    return attributes


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda x: f"user_{x}")
    email = factory.lazy_attribute(lambda x: f"{x.username}@test.com")
    password = factory.LazyAttribute(lambda obj: f"{obj.username}_password")
    is_active = None
    is_superuser = None


def create_factory_users(users_qty: int, password: str = "_password", **kwargs) -> Dict[UserFactory, str]:
    users_dict: Dict[Dict[str, List[UserFactory]], Dict[str, List[str]]] = {"users": list(), "password_list": list()}
    for count in range(users_qty):
        clean_password = f"{count}{password}"
        user = UserFactory(password=get_password_hash(clean_password), **kwargs)

        users_dict["users"].append(user)
        users_dict["password_list"].append(clean_password)
    return users_dict
