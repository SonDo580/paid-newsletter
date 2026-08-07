import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.schemas.auth import TokenType, TokenPayload
from app.config.settings import settings
from app.utils.datetime import datetime_utils


class TokenUtils:
    def __init__(self, algorithm="HS256"):
        self.algorithm = algorithm
        self.secret_key_map = {
            TokenType.MAGIC: settings.MAGIC_TOKEN_SECRET_KEY,
            TokenType.ACCESS: settings.ACCESS_TOKEN_SECRET_KEY,
        }
        self.expires_delta_map = {
            TokenType.MAGIC: timedelta(minutes=settings.MAGIC_TOKEN_EXPIRES_MINUTES),
            TokenType.ACCESS: timedelta(days=settings.ACCESS_TOKEN_EXPIRES_DAYS),
        }

    def get_expires_at(self, type: TokenType) -> datetime:
        expires_delta = self.expires_delta_map[type]
        return datetime_utils.now_utc() + expires_delta

    def generate_token(self, payload: TokenPayload) -> str:
        secret_key = self.secret_key_map[payload.type]
        return jwt.encode(
            payload=payload.model_dump(exclude_none=True),
            key=secret_key,
            algorithm=self.algorithm,
        )

    def verify_token(self, token: str, expected_type: TokenType) -> TokenPayload:
        secret_key = self.secret_key_map[expected_type]
        try:
            payload_dict = jwt.decode(
                jwt=token, key=secret_key, algorithms=[self.algorithm]
            )
            payload = TokenPayload.model_validate(payload_dict)
            if payload.type != expected_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )


token_utils = TokenUtils()
