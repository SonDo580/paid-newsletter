from fastapi import Request, HTTPException, status, Depends
from typing import Optional

from app.config.settings import settings
from app.common.constants import CookieKey
from app.db.connect import DBSessionDep
from app.db.models.reader import Reader
from app.schemas.auth import CurrentUser, TokenType
from app.services.auth import AuthService
from app.services.readers import ReadersService
from app.utils.token import token_utils


async def _get_current_email(request: Request) -> str:
    token = request.cookies.get(CookieKey.ACCESS_TOKEN)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    payload = token_utils.verify_token(token, expected_type=TokenType.ACCESS)
    return payload.sub


async def get_current_user(
    db_session: DBSessionDep,
    email: str = Depends(_get_current_email),
) -> CurrentUser:
    is_admin = AuthService.is_admin(email)
    reader: Optional[Reader] = None
    if not is_admin:
        reader = ReadersService.get_by_email(db_session, email)
        if not reader or not reader.verified_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reader not found or unverified",
            )
    return CurrentUser(email=email, is_admin=is_admin, reader=reader)


async def admin_required(user: CurrentUser = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
