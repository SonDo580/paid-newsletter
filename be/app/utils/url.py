from urllib.parse import urlencode
from typing import Optional

from app.config.settings import settings


class UrlBuilder:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/"

    def build(self, path: str, query: Optional[dict] = None) -> str:
        url = self.base_url + path.lstrip("/")
        if query:
            clean_query = {k: v for k, v in query.items() if v is not None}
            if clean_query:
                query_str = urlencode(clean_query, doseq=True)
                url = f"{url}?{query_str}"
        return url


api_url_builder = UrlBuilder(base_url=settings.API_URL)
