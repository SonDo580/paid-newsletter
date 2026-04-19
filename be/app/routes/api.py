from fastapi import APIRouter

from app.routes import auth, articles

api_router = APIRouter()

# Gather sub-routers
api_router.include_router(auth.router)
api_router.include_router(articles.router)
