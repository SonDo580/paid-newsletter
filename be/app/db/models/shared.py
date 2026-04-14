from sqlmodel import SQLModel
from pydantic import ConfigDict
import sqlalchemy.types as sa_types
from typing import Optional
from datetime import datetime, timezone

from app.utils.datetime import datetime_utils


class StrictModel(SQLModel):
    model_config = ConfigDict(validate_assignment=True)


class UTCDateTime(sa_types.TypeDecorator):
    """SQLite doesn't support timezone-aware datetime -> always use UTC
    - convert to UTC & store in SQLite as naive.
    - attach UTC tzinfo & return to Python as tz-aware.
    """

    impl = sa_types.DateTime
    cache_ok = True

    def process_bind_param(
        self, value: Optional[datetime], dialect
    ) -> Optional[datetime]:
        """Runs when SAVING data."""
        # Convert to UTC and make naive for storage
        return (
            None if value is None else datetime_utils.to_utc(value).replace(tzinfo=None)
        )

    def process_result_value(
        self, value: Optional[datetime], dialect
    ) -> Optional[datetime]:
        """Runs when LOADING data."""
        # Attach UTC tzinfo to the naive datetime
        return None if value is None else value.replace(tzinfo=timezone.utc)
