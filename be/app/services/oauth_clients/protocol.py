from typing import Protocol

from app.schemas.auth import OAuthUserInfo


class OAuthProviderClient(Protocol):
    def get_authorization_url(self, state: str) -> str: ...
    def get_user_info(self, code: str) -> OAuthUserInfo: ...
