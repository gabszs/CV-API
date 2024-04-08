import pytest
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


@pytest.mark.asyncio
async def test_session_query(session):
    assert isinstance(session, AsyncSession)

    result = await session.execute(select(User))
    users = result.scalars().all()

    assert len(users) == 0


@pytest.mark.asyncio
async def test_session_with_users(session, user, other_user):
    assert isinstance(session, AsyncSession)

    result = await session.execute(select(User))
    users = result.scalars().all()

    assert len(users) == 2


def test_app_fixture(app):
    assert isinstance(app, FastAPI)
    assert app.title == "CV-Api"
    assert app.description == "CV Managment Web api with basic auth crud built by @GabrielCarvalho to my girlfriend"
    assert app.contact["name"] == "Gabriel Carvalho"
    assert app.contact["url"] == "https://www.linkedin.com/in/gabzsz/"
    assert app.contact["email"] == "gabriel.carvalho@huawei.com"
    assert (
        app.summary == "WebApi build on best market practices such as TDD, Clean Arch, Data Validation with Pydantic V2"
    )
