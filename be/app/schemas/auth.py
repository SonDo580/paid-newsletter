from pydantic import BaseModel
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

from app.db.models.reader import Reader


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
