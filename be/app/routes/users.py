from fastapi import APIRouter

from app.schemas.users import GetMeResBody, PublicReader
from app.dependencies.auth import CurrentUserDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=GetMeResBody)
def get_me(current_user: CurrentUserDep):
    public_reader = None
    if current_user.reader:
        public_reader = PublicReader(
            **current_user.reader.model_dump(),
            has_stripe_profile=bool(current_user.reader.stripe_customer_id),
        )
    return GetMeResBody(
        email=current_user.email,
        is_admin=current_user.is_admin,
        reader=public_reader,
    )
