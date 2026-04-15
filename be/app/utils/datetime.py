from datetime import datetime, timezone


UTC_TZ = timezone.utc


class DateTimeUtils:
    def now_utc(self) -> datetime:
        return datetime.now(tz=UTC_TZ)

    def to_utc(self, dt: datetime) -> datetime:
        """Convert tz-aware datetime to UTC."""
        self._require_tz_aware(dt)
        return dt.astimezone(UTC_TZ)

    def _require_tz_aware(self, dt: datetime):
        if dt.tzinfo is None:
            raise ValueError(
                "Cannot convert naive datetime. Timezone info is required."
            )


datetime_utils = DateTimeUtils()
