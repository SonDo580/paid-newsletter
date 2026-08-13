from arq.connections import RedisSettings
from arq import ArqRedis, Retry
from sqlmodel import Session as DBSession, exists, or_, select, literal, update
from sqlalchemy.dialects.sqlite import insert
from loguru import logger
from enum import Enum
from datetime import timedelta

from app.config.settings import settings
from app.config.sdks import init_sdks
from app.db.connect import engine
from app.db.models.article import Article
from app.db.models.reader import Reader
from app.db.models.notification import Notification
from app.db.models.subscription import Subscription, SubscriptionStatus
from app.services.mail import MailService
from app.utils.datetime import datetime_utils


class TaskName(str, Enum):
    CREATE_ARTICLE_NOTIFICATIONS = "task_create_article_notifications"
    SEND_ARTICLE_NOTIFICATIONS = "task_send_article_notifications"


async def task_create_article_notifications(ctx: dict, article_id: int):
    base_msg = (
        f"[Task {TaskName.CREATE_ARTICLE_NOTIFICATIONS.value}] article_id={article_id}"
    )
    logger.info(f"{base_msg}: Starting...")

    with DBSession(engine) as db_session:
        article = db_session.get(Article, article_id)
        if not article or not article.is_published:
            return

        # Subquery checking if reader has active/trialing subscription
        active_subscription_exists = exists().where(
            Subscription.reader_id == Reader.id,
            or_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.status == SubscriptionStatus.TRIALING,
            ),
        )

        # SELECT statement producing values to insert
        now = datetime_utils.now_utc()
        select_subquery = select(
            literal(article_id).label("article_id"),
            Reader.id.label("reader_id"),
            literal(now).label("created_at"),
        ).where(active_subscription_exists)

        # Insert notifications to send to active subscribers
        insert_stmt = (
            insert(Notification)
            .from_select(["article_id", "reader_id", "created_at"], select_subquery)
            .on_conflict_do_nothing(index_elements=["article_id", "reader_id"])
        )
        db_session.exec(insert_stmt)
        db_session.commit()

    # Trigger send task
    arq_redis: ArqRedis = ctx["redis"]
    await arq_redis.enqueue_job(
        TaskName.SEND_ARTICLE_NOTIFICATIONS, article_id=article_id
    )

    logger.info(f"{base_msg}: Done")


async def task_send_article_notifications(ctx: dict, article_id: int):
    base_msg = (
        f"[Task {TaskName.SEND_ARTICLE_NOTIFICATIONS.value}] article_id={article_id}"
    )
    logger.info(f"{base_msg}: Starting...")

    mail_service = MailService()

    with DBSession(engine) as db_session:
        article = db_session.get(Article, article_id)
        if not article or not article.is_published:
            return

        batch_size = 500
        last_notification_id = 0

        while True:
            # Find unsent notifications
            stmt = (
                select(Notification.id, Reader.email)
                .join(Reader, Notification.reader_id == Reader.id)
                .where(
                    Notification.article_id == article_id,
                    Notification.sent_at.is_(None),
                    Notification.id > last_notification_id,
                )
                .order_by(Notification.id.asc())
                .limit(batch_size)
            )
            results = db_session.exec(stmt).all()
            if not results:
                break

            notification_ids = [row[0] for row in results]
            emails = [row[1] for row in results]

            # Send emails
            try:
                mail_service.bulk_send_article_notifications(
                    emails, notification_ids, article
                )
                logger.info(f"{base_msg}: Sent {len(emails)} emails")
            except Exception as e:
                logger.exception(f"{base_msg}: Email batch failed: {e}")
                raise Retry(defer=timedelta(seconds=15))

            # Mark notifications as sent
            now = datetime_utils.now_utc()
            update_stmt = (
                update(Notification)
                .where(Notification.id.in_(notification_ids))
                .values(sent_at=now)
            )
            db_session.exec(update_stmt)
            db_session.commit()

            last_notification_id = notification_ids[-1]

    logger.info(f"{base_msg}: Done")


async def startup(ctx: dict):
    init_sdks()


class WorkerSettings:
    functions = [task_create_article_notifications, task_send_article_notifications]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_retries = 5
    on_startup = startup
