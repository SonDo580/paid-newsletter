from pydantic import BaseModel
from datetime import datetime

from app.db.models.subscription import SubscriptionStatus


class SubscriptionSummary(BaseModel):
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
