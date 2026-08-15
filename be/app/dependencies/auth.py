from fastapi import Request, HTTPException, status, Depends
from typing import Optional, Annotated

from app.common.constants import CookieKey
from app.db.models.reader import Reader
from app.schemas.auth import CurrentUser, TokenType
from app.utils.token import token_utils
from app.dependencies.services import AuthServiceDep, ReadersServiceDep


def get_current_user(
    request: Request,
    auth_service: AuthServiceDep,
    readers_service: ReadersServiceDep,
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
    is_admin = auth_service.is_admin(email)
    reader: Optional[Reader] = None
    if not is_admin:
        reader = readers_service.get_by_email(email)
        if not reader or not reader.verified_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reader not found or unverified",
            )

    return CurrentUser(email=email, is_admin=is_admin, reader=reader)


def get_optional_user(
    request: Request,
    auth_service: AuthServiceDep,
    readers_service: ReadersServiceDep,
) -> Optional[CurrentUser]:
    # Verify access token and extract email for authorized user
    token = request.cookies.get(CookieKey.ACCESS_TOKEN)
    if not token:
        return None
    payload = token_utils.verify_token(token, expected_type=TokenType.ACCESS)
    email = payload.sub

    # Find reader by email if user is reader
    is_admin = auth_service.is_admin(email)
    reader: Optional[Reader] = None
    if not is_admin:
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


def get_optional_reader(
    user: Optional[CurrentUser] = Depends(get_optional_user),
) -> Optional[Reader]:
    if not user:
        return None
    if user.is_admin or not user.reader:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only for reader"
        )
    return user.reader


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
OptionalUserDep = Annotated[Optional[CurrentUser], Depends(get_optional_user)]
CurrentReaderDep = Annotated[Reader, Depends(get_current_reader)]
OptionalReaderDep = Annotated[Optional[Reader], Depends(get_optional_reader)]
AdminRequiredDep = Annotated[None, Depends(admin_required)]
