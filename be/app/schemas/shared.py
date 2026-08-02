from typing import Annotated
from pydantic import BeforeValidator
from enum import Enum

TStrippedStr = Annotated[
    str,
    BeforeValidator(lambda v: v.strip()),
]


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
