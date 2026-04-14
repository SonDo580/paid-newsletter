from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routes.api import api_router
from app.config.openapi import setup_openapi
from app.common.exceptions import register_exception_handlers

app = FastAPI(title="Paid Newsletter API")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


app.include_router(api_router, prefix="/api")
register_exception_handlers(app)
setup_openapi(app)
