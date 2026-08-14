from typing import Optional
from fastapi import HTTPException, status
from sqlmodel import Session as DBSession, select
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config.settings import settings
from app.db.models.oauth_account import OAuthProvider, OAuthAccount
from app.db.models.reader import Reader
from app.services.oauth_clients.protocol import OAuthProviderClient
from app.schemas.auth import OAuthStatePayload, OAuthUserInfo


class OAuthService:
    def __init__(
        self,
        db_session: DBSession,
        provider_clients: dict[OAuthProvider, OAuthProviderClient],
    ):
        self.db_session = db_session
        self.provider_clients = provider_clients
        self._state_serializer = URLSafeTimedSerializer(
            secret_key=settings.OAUTH_STATE_SECRET_KEY,
            salt="oauth-state-salt",
        )

    def get_provider_client(self, provider: OAuthProvider) -> OAuthProviderClient:
        client = self.provider_clients.get(provider)
        if not client:
            provider_name = provider.value.title()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider_name}",
            )
        return client

    def generate_state(self, payload: OAuthStatePayload) -> str:
        return self._state_serializer.dumps(payload.model_dump(exclude_none=True))

    def verify_state(self, state: str) -> OAuthStatePayload:
        try:
            payload_dict = self._state_serializer.loads(
                state, max_age=settings.OAUTH_STATE_EXPIRES_MINUTES * 60
            )
            return OAuthStatePayload.model_validate(payload_dict)
        except SignatureExpired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth state token expired",
            )
        except BadSignature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth state parameter",
            )

    def get_reader_by_oauth_info(self, info: OAuthUserInfo) -> Optional[Reader]:
        stmt = (
            select(Reader)
            .join(OAuthAccount, Reader.id == OAuthAccount.reader_id)
            .where(
                OAuthAccount.provider == info.provider,
                OAuthAccount.provider_account_id == info.provider_account_id,
            )
        )
        return self.db_session.exec(stmt).first()

    def __get_oauth_account_by_account_id(
        self, provider: OAuthProvider, provider_account_id: str
    ) -> Optional[OAuthAccount]:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id,
        )
        return self.db_session.exec(stmt).first()

    def __get_oauth_account_for_reader(
        self, provider: OAuthProvider, reader: Reader
    ) -> Optional[OAuthAccount]:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.reader_id == reader.id,
        )
        return self.db_session.exec(stmt).first()

    def link_account(self, reader: Reader, info: OAuthUserInfo):
        existing = self.__get_oauth_account_by_account_id(
            provider=info.provider, provider_account_id=info.provider_account_id
        )
        if existing:
            if existing.reader_id == reader.id:
                return  # Account is already linked to current user
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This account is already linked to another user",
            )

        existing = self.__get_oauth_account_for_reader(
            provider=info.provider, reader=reader
        )
        if existing:
            provider_name = info.provider.value.title()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a {provider_name} account linked",
            )

        try:
            account = OAuthAccount(
                reader_id=reader.id,
                provider=info.provider,
                provider_account_id=info.provider_account_id,
                email=info.email,
            )
            self.db_session.add(account)
            self.db_session.commit()
        except Exception:
            self.db_session.rollback()
            raise
