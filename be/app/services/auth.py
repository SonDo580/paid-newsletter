from sqlmodel import Session as DBSession

from app.config.settings import settings
from app.services.readers import ReadersService
from app.schemas.auth import TokenPayload, TokenType
from app.utils.token import token_utils


class AuthService:
    def __init__(self, db_session: DBSession):
        self.db_session = db_session
        self.readers_service = ReadersService(self.db_session)

    def login(
        self, email: str, redirect_path: str
    ) -> str:
        # Register reader automatically
        if not self.is_admin(email):
            self.readers_service.get_by_email_or_create(email)

        # Generate magic token
        token_payload = TokenPayload(
            sub=email,
            exp=token_utils.get_expires_at(TokenType.MAGIC),
            type=TokenType.MAGIC,
            redirect_path=redirect_path,
        )
        token = token_utils.generate_token(token_payload)
        return token

    def verify(self, token: str) -> tuple[str,str]:
        # Verify Magic Token
        magic_token_payload = token_utils.verify_token(
            token, expected_type=TokenType.MAGIC
        )
        email = magic_token_payload.sub

        # Ensure reader is verified
        if not self.is_admin(email):
            self.readers_service.verify_reader(email)

        # Issue access token
        access_token_payload = TokenPayload(
            sub=email,
            exp=token_utils.get_expires_at(TokenType.ACCESS),
            type=TokenType.ACCESS,
        )
        access_token = token_utils.generate_token(access_token_payload)

        redirect_path = magic_token_payload.redirect_path or "/"
        return access_token, redirect_path

    def is_admin(self, email: str) -> bool:
        return email == settings.ADMIN_EMAIL
