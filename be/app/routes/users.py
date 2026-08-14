from fastapi import APIRouter

from app.schemas.users import GetMeResBody, PublicReader, PublicOAuthAccount
from app.dependencies.auth import CurrentUserDep
from app.dependencies.services import OAuthServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=GetMeResBody)
def get_me(current_user: CurrentUserDep, oauth_service: OAuthServiceDep):
    public_reader = None
    if current_user.reader:
        oauth_accounts = oauth_service.get_all_oauth_accounts_for_reader(
            current_user.reader
        )
        public_oauth_accounts = [
            PublicOAuthAccount(
                provider=acc.provider,
                identifier=acc.email or acc.provider_account_id,
            )
            for acc in oauth_accounts
        ]
        public_reader = PublicReader(
            **current_user.reader.model_dump(),
            has_stripe_profile=bool(current_user.reader.stripe_customer_id),
            oauth_accounts=public_oauth_accounts
        )
    return GetMeResBody(
        email=current_user.email,
        is_admin=current_user.is_admin,
        reader=public_reader,
    )
