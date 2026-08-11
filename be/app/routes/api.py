from fastapi import APIRouter

from app.routes import auth, articles, users, payments, subscriptions

api_router = APIRouter()

# Gather sub-routers
api_router.include_router(articles.router)
api_router.include_router(auth.router)
api_router.include_router(payments.router)
api_router.include_router(users.router)
api_router.include_router(subscriptions.router)
