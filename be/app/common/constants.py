from enum import Enum


class Env(str, Enum):
    LOCAL = "local"
    PROD = "prod"


class CookieKey(str, Enum):
    ACCESS_TOKEN = "access_token"


class HeaderKey(str, Enum):
    RETRY_AFTER = "Retry-After"
