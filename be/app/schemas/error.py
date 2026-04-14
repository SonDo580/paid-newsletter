from pydantic import BaseModel
from typing import Optional, Any


class ErrResBody(BaseModel):
    message: str
    detail: Optional[Any] = None
