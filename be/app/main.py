from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes.api import api_router
from app.config.settings import settings
from app.config.sdks import init_sdks
from app.config.openapi import setup_openapi
from app.common.exceptions import register_exception_handlers
from app.common.arq_redis import init_arq_redis, close_arq_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_sdks()
    await init_arq_redis()

    yield

    await close_arq_redis()


app = FastAPI(lifespan=lifespan, title="Paid Newsletter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.STATIC_PREFIX,
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="static",
)

app.include_router(api_router, prefix=settings.API_PREFIX)

setup_openapi(app)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
