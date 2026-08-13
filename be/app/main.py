from fastapi import FastAPI
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

app.include_router(api_router, prefix="/api")
register_exception_handlers(app)
setup_openapi(app)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
