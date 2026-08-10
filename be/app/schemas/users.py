from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.auth import CurrentUser


class SubscriptionSummary(BaseModel):
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    is_active: bool
    is_past_due: bool


class UserProfileResBody(CurrentUser):
    subscription: Optional[SubscriptionSummary] = None
