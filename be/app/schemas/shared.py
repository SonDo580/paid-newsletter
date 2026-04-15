from typing import Annotated
from pydantic import BeforeValidator

TStrippedStr = Annotated[
    str,
    BeforeValidator(lambda v: v.strip()),
]
