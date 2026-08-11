from fastapi import APIRouter

from app.schemas.auth import CurrentUser
from app.dependencies.auth import CurrentUserDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=CurrentUser)
def get_me(current_user: CurrentUserDep):
    return current_user
