from fastapi import APIRouter

from app.routes import articles, auth, images, payments, subscriptions, users

api_router = APIRouter()

# Gather sub-routers
api_router.include_router(auth.router)
api_router.include_router(articles.router)
api_router.include_router(images.router)
api_router.include_router(payments.router)
api_router.include_router(subscriptions.router)
api_router.include_router(users.router)
