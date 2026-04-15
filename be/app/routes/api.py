from fastapi import APIRouter

from app.routes import articles

api_router = APIRouter()

# Gather sub-routers
api_router.include_router(articles.router)
