from pydantic import BaseModel, Field
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional

from app.db.models.reader import Reader


class LoginReqBody(BaseModel):
    email: EmailStr
    redirect_path: Optional[str] = None

class TokenType(str, Enum):
    MAGIC = "magic"
    ACCESS = "access"


class TokenPayload(BaseModel):
    sub: str = Field(description="email")
    exp: datetime
    type: TokenType
    redirect_path: Optional[str] = None


class CurrentUser(BaseModel):
    """Currently logged-in user (admin or reader)"""

    email: str
    is_admin: bool
    reader: Optional[Reader] = None
