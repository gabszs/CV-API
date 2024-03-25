import factory

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
    password = factory.Faker("password", length=12)
