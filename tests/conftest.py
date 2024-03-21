import pytest
from app.core.database import Database
from app.models import User
import factory
from tests.factories import UserFactory

@pytest.fixture
def session():
    db = Database('sqlite:///:memory:')
    db.create_database()

    with db.session() as session:
        yield session


@pytest.fixture
def user_instance():
    return UserFactory()


# username
# password
# email