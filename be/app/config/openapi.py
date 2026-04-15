from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.schemas.error import ErrResBody


def setup_openapi(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        app.openapi_schema = get_openapi(
            title=app.title,
            version="0.1.0",
            routes=app.routes,
        )

        app.openapi_schema["components"]["schemas"][
            "ErrResBody"
        ] = ErrResBody.model_json_schema()

        return app.openapi_schema

    app.openapi = custom_openapi
