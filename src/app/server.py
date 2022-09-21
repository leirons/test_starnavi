from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware

from app.routers import users
from app.routers import post
from core.middlewares.authentication import (AuthBackend,
                                             AuthenticationMiddleware)


def init_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routers(app: FastAPI) -> None:
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(post.router, prefix="/api/v1")


def init_middleware(app: FastAPI) -> None:
    app.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
    app.add_middleware(SessionMiddleware, secret_key="SECRET")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pet Store Server",
        description="API",
        version="1.0.0",
        docs_url="/docs",
    )
    init_routers(app=app)
    init_cors(app=app)
    init_middleware(app=app)
    return app


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    tags_desc_list = [
        {"name": "user", "description": "Operations about user"},
        {"name": "post", "description": "Operations about post"},

    ]
    openapi_schema = get_openapi(
        title="Test Project",
        version="1.0",
        routes=app.routes,
        description="This is a sample Test",
    )
    openapi_schema["tags"] = tags_desc_list
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = create_app()
app.openapi = custom_openapi



