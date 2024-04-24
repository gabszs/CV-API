from typing import Dict
from typing import List

import factory

from app.core.security import get_password_hash
from app.models import User
from app.schemas.user_schema import UserWithCleanPassword


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
    users_dict: Dict[Dict[str, List[UserFactory]], Dict[str, List[str]]] = {"users": list(), "clean_users": list()}
    for count in range(users_qty):
        clean_password = f"{count}{password}"
        user = UserFactory(password=get_password_hash(clean_password), **kwargs)
        clean_user = UserWithCleanPassword(
            email=user.email, username=user.email, password=user.password, clean_password=clean_password
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
