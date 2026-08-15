from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

from app.db.models.reader import Reader
from app.db.models.oauth_account import OAuthProvider


class LoginReqBody(BaseModel):
    email: EmailStr
    redirect_path: str = "/"


class TokenType(str, Enum):
    MAGIC = "magic"
    ACCESS = "access"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: TokenType
    redirect_path: Optional[str] = None


class CurrentUser(BaseModel):
    """Currently logged-in user (admin or reader)"""

    email: str
    is_admin: bool
    reader: Optional[Reader] = None


class OAuthAction(str, Enum):
    LOGIN = "login"
    CONNECT = "connect"


class OAuthAuthorizeParams(BaseModel):
    """Query parameters passed by FE."""

    action: OAuthAction
    redirect_path: str = "/"


class OAuthCallbackParams(BaseModel):
    """Query parameters passed by OAuth provider."""

    code: str
    state: str


class OAuthStatePayload(BaseModel):
    """Payload serialized and signed as 'state'."""

    action: OAuthAction
    redirect_path: str
    provider: OAuthProvider


class OAuthUserInfo(BaseModel):
    provider: OAuthProvider
    provider_account_id: str
    email: Optional[str] = None
