from sqlmodel import Session as DBSession

from app.config.settings import settings
from app.services.readers import ReadersService
from app.schemas.auth import TokenPayload, TokenType
from app.utils.token import token_utils


class AuthService:
    @staticmethod
    def login(db_session: DBSession, email: str) -> str:
        # Register reader automatically
        if not AuthService.is_admin(email):
            ReadersService.get_by_email_or_create(db_session, email)

        # Generate magic token
        token_payload = TokenPayload(
            sub=email,
            exp=token_utils.get_expires_at(TokenType.MAGIC),
            type=TokenType.MAGIC,
        )
        token = token_utils.generate_token(token_payload)
        return token

    @staticmethod
    def verify(db_session: DBSession, token: str) -> str:
        # Verify Magic Token
        magic_token_payload = token_utils.verify_token(
            token, expected_type=TokenType.MAGIC
        )
        email = magic_token_payload.sub

        # Ensure reader is verified
        if not AuthService.is_admin(email):
            ReadersService.verify_reader(db_session, email)

        # Issue access token
        access_token_payload = TokenPayload(
            sub=email,
            exp=token_utils.get_expires_at(TokenType.ACCESS),
            type=TokenType.ACCESS,
        )
        access_token = token_utils.generate_token(access_token_payload)
        return access_token

    @staticmethod
    def is_admin(email: str) -> bool:
        return email == settings.ADMIN_EMAIL
