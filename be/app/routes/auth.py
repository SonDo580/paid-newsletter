from fastapi import APIRouter, status
from fastapi.responses import Response, RedirectResponse

from app.config.settings import settings
from app.common.constants import Env, CookieKey
from app.db.connect import DBSessionDep
from app.services.auth import AuthService
from app.services.mail import MailService
from app.schemas.auth import LoginReqBody
from app.utils.url import fe_url_builder

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
def login(data: LoginReqBody, db_session: DBSessionDep):
    token = AuthService.login(db_session, data.email, data.redirect_path)
    expires_in_str = f"{settings.MAGIC_TOKEN_EXPIRES_MINUTES} minutes"
    MailService.send_magic_link(data.email, token, expires_in_str)


@router.get("/verify", response_class=RedirectResponse)
def verify(token: str, db_session: DBSessionDep):
    access_token, redirect_path = AuthService.verify(db_session, token)
    redirect_url = fe_url_builder.build(redirect_path)
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        key=CookieKey.ACCESS_TOKEN.value,
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=settings.ENV != Env.LOCAL,
        max_age=settings.ACCESS_TOKEN_EXPIRES_DAYS * 86400,  # seconds
    )
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=CookieKey.ACCESS_TOKEN.value,
        httponly=True,
        samesite="lax",
        secure=settings.ENV != Env.LOCAL,
        path="/",
    )
