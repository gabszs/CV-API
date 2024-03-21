from datetime import datetime

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

    # Definindo os atributos da fábrica
    # id = datetime.now()
    email = factory.Sequence(lambda n: f"user{n}@example.com")  # Gera emails fictícios sequenciais
    username = factory.Sequence(lambda n: f"user{n}")  # Gera usernames fictícios sequenciais
    password = factory.Faker("password")  # Gera senhas fictícias
    created_at = datetime.now()  # Define o valor padrão de created_at
    updated_at = datetime.now()
