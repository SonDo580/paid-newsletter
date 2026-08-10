from fastapi import Request, HTTPException, status, Depends
from typing import Optional

from app.common.constants import CookieKey
from app.db.connect import DBSessionDep
from app.db.models.reader import Reader
from app.schemas.auth import CurrentUser, TokenType
from app.services.auth import AuthService
from app.services.readers import ReadersService
from app.utils.token import token_utils


def get_current_user(
    request: Request,
    db_session: DBSessionDep,
) -> CurrentUser:
    # Verify access token and extract email
    token = request.cookies.get(CookieKey.ACCESS_TOKEN)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    payload = token_utils.verify_token(token, expected_type=TokenType.ACCESS)
    email = payload.sub

    # Find reader by email if user is reader
    auth_service = AuthService(db_session) 
    is_admin = auth_service.is_admin(email)
    reader: Optional[Reader] = None
    if not is_admin:
        readers_service = ReadersService(db_session)
        reader = readers_service.get_by_email(email)
        if not reader or not reader.verified_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reader not found or unverified",
            )

    return CurrentUser(email=email, is_admin=is_admin, reader=reader)


def get_optional_user(
    request: Request,
    db_session: DBSessionDep,
) -> Optional[CurrentUser]:
    # Verify access token and extract email for authorized user
    token = request.cookies.get(CookieKey.ACCESS_TOKEN)
    if not token:
        return None
    payload = token_utils.verify_token(token, expected_type=TokenType.ACCESS)
    email = payload.sub

    # Find reader by email if user is reader
    auth_service = AuthService(db_session) 
    is_admin = auth_service.is_admin(email)
    reader: Optional[Reader] = None
    if not is_admin:
        readers_service = ReadersService(db_session)
        reader = readers_service.get_by_email(email)
        if not reader or not reader.verified_at:
            return None

    return CurrentUser(email=email, is_admin=is_admin, reader=reader)


def admin_required(user: CurrentUser = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )


def get_current_reader(user: CurrentUser = Depends(get_current_user)) -> Reader:
    if user.is_admin or not user.reader:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for reader"
        )
    return user.reader
