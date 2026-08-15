import requests
from fastapi import HTTPException, status
from loguru import logger
from pydantic import BaseModel

from app.config.settings import settings
from app.schemas.auth import OAuthUserInfo
from app.db.models.oauth_account import OAuthProvider
from app.utils.url import UrlBuilder


class GoogleTokenResponse(BaseModel):
    access_token: str
    # ... other unused fields


class GoogleUserInfoResponse(BaseModel):
    sub: str
    email: str
    # ... other unused fields


class GoogleOAuthProviderClient:
    """Implement OAuthProviderClient protocol."""

    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(
        self,
        client_id: str = settings.GOOGLE_CLIENT_ID,
        client_secret: str = settings.GOOGLE_CLIENT_SECRET,
        redirect_uri: str = settings.GOOGLE_REDIRECT_URI,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
        return UrlBuilder(base_url=self.AUTHORIZE_URL).build(path="", query=params)

    def get_user_info(self, code: str) -> OAuthUserInfo:
        # Exchange authorization code for tokens
        tokens_payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        tokens_res = requests.post(self.TOKEN_URL, data=tokens_payload)
        if tokens_res.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to exchange token with Google: {tokens_res.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange token with Google",
            )
        tokens_data = GoogleTokenResponse.model_validate(tokens_res.json())

        # Get user data
        user_res = requests.get(
            self.USER_INFO_URL,
            headers={"Authorization": f"Bearer {tokens_data.access_token}"},
        )
        if user_res.status_code != status.HTTP_200_OK:
            logger.error(f"Failed to fetch user info from Google: {user_res.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user profile from Google",
            )
        user_data = GoogleUserInfoResponse.model_validate(user_res.json())

        return OAuthUserInfo(
            provider=OAuthProvider.GOOGLE,
            provider_account_id=user_data.sub,
            email=user_data.email,
        )
