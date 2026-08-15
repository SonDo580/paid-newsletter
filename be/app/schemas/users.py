from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.db.models.oauth_account import OAuthProvider


class PublicOAuthAccount(BaseModel):
    provider: OAuthProvider
    identifier: str


class PublicReader(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime
    verified_at: datetime
    has_stripe_profile: bool = False
    oauth_accounts: list[PublicOAuthAccount] = []


class GetMeResBody(BaseModel):
    email: str
    is_admin: bool
    reader: Optional[PublicReader] = None
