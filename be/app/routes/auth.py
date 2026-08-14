from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response, RedirectResponse
from typing import Optional

from app.config.settings import settings
from app.common.constants import Env, CookieKey
from app.schemas.auth import (
    LoginReqBody,
    OAuthAuthorizeParams,
    OAuthAction,
    OAuthStatePayload,
    OAuthCallbackParams,
    OAuthUserInfo,
)
from app.db.models.oauth_account import OAuthProvider
from app.db.models.reader import Reader
from app.utils.url import fe_url_builder
from app.dependencies.auth import OptionalReaderDep
from app.dependencies.services import AuthServiceDep, MailServiceDep, OAuthServiceDep
from app.services.oauth import OAuthService
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(
    data: LoginReqBody, auth_service: AuthServiceDep, mail_service: MailServiceDep
):
    token = auth_service.login(data.email, data.redirect_path)
    expires_in_str = f"{settings.MAGIC_TOKEN_EXPIRES_MINUTES} minutes"
    mail_service.send_magic_link(data.email, token, expires_in_str)


@router.get("/verify", response_class=RedirectResponse)
def verify(token: str, auth_service: AuthServiceDep):
    access_token, redirect_path = auth_service.verify(token)
    redirect_url = fe_url_builder.build(redirect_path)
    response = RedirectResponse(url=redirect_url)
    _set_access_token_cookie(response, access_token)
    return response


def _set_access_token_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key=CookieKey.ACCESS_TOKEN.value,
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=settings.ENV != Env.LOCAL,
        max_age=settings.ACCESS_TOKEN_EXPIRES_DAYS * 86400,  # seconds
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=CookieKey.ACCESS_TOKEN.value,
        httponly=True,
        samesite="lax",
        secure=settings.ENV != Env.LOCAL,
        path="/",
    )


@router.get("/{provider}/authorize", response_class=RedirectResponse)
def oauth_authorize(
    provider: OAuthProvider,
    current_reader: OptionalReaderDep,
    oauth_service: OAuthServiceDep,
    params: OAuthAuthorizeParams = Depends(),
):
    if params.action == OAuthAction.CONNECT and not current_reader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in to connect social account",
        )

    if params.action == OAuthAction.LOGIN and current_reader:
        return RedirectResponse(url=fe_url_builder.build(params.redirect_path))

    provider_client = oauth_service.get_provider_client(provider)
    state = oauth_service.generate_state(
        OAuthStatePayload(
            action=params.action, redirect_path=params.redirect_path, provider=provider
        )
    )
    auth_url = provider_client.get_authorization_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/{provider}/callback", response_class=RedirectResponse)
def oauth_callback(
    provider: OAuthProvider,
    oauth_service: OAuthServiceDep,
    auth_service: AuthServiceDep,
    current_reader: OptionalReaderDep,
    params: OAuthCallbackParams = Depends(),
):
    state_payload = oauth_service.verify_state(params.state)
    if state_payload.provider != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth provider mismatch in state",
        )

    provider_client = oauth_service.get_provider_client(provider)
    oauth_user_info = provider_client.get_user_info(params.code)

    if state_payload.action == OAuthAction.CONNECT:
        return _handle_oauth_connect(
            oauth_service=oauth_service,
            current_reader=current_reader,
            oauth_user_info=oauth_user_info,
            redirect_path=state_payload.redirect_path,
        )
    elif state_payload.action == OAuthAction.LOGIN:
        return _handle_oauth_login(
            auth_service=auth_service,
            oauth_service=oauth_service,
            oauth_user_info=oauth_user_info,
            redirect_path=state_payload.redirect_path,
        )
    raise Exception("unreachable")


def _handle_oauth_connect(
    oauth_service: OAuthService,
    current_reader: Optional[Reader],
    oauth_user_info: OAuthUserInfo,
    redirect_path: str,
) -> RedirectResponse:
    if not current_reader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired while connecting account",
        )

    oauth_service.link_account(current_reader, oauth_user_info)
    redirect_url = fe_url_builder.build(redirect_path)
    return RedirectResponse(url=redirect_url)


def _handle_oauth_login(
    auth_service: AuthService,
    oauth_service: OAuthService,
    oauth_user_info: OAuthUserInfo,
    redirect_path: str,
) -> RedirectResponse:
    reader = oauth_service.get_reader_by_oauth_info(oauth_user_info)
    if not reader:
        provider_name = oauth_user_info.provider.value.title()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You haven't connected {provider_name} account",
        )

    access_token = auth_service.issue_access_token(reader.email)
    redirect_url = fe_url_builder.build(redirect_path)
    response = RedirectResponse(url=redirect_url)
    _set_access_token_cookie(response, access_token)
    return response
