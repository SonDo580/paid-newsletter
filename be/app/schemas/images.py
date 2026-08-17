from pydantic import BaseModel


class UploadResBody(BaseModel):
    url: str
