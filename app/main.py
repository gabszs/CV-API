from fastapi import FastAPI

from app.routes.v1 import routers

app = FastAPI(
    title="CV-Api",
    description="CV Managment Web api with basic auth crud built by @GabrielCarvalho to my girlfriend",
    contact={
        "name": "Gabriel Carvalho",
        "url": "https://www.linkedin.com/in/gabzsz/",
        "email": "gabriel.carvalho@huawei.com",
    },
    summary="WebApi build on best market practices such as TDD, Clean Arch, Data Validation with Pydantic V2",
)

app.include_router(routers)
