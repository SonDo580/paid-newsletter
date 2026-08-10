from app.schemas.auth import CurrentUser


class UserProfileResBody(CurrentUser):
    has_active_subscription: bool
