import resend
from jinja2 import Environment, PackageLoader, select_autoescape
import re
import hashlib

from app.config.settings import settings
from app.db.models.article import Article
from app.utils.url import api_url_builder, fe_url_builder

jinja2_env = Environment(
    loader=PackageLoader("app", "templates/emails"),
    autoescape=select_autoescape(["html", "xml"]),
)


class MailService:
    def __render_template(self, template_name: str, **context) -> str:
        template = jinja2_env.get_template(template_name)
        return template.render(**context)

    def __normalize_for_delivery(self, email: str) -> str:
        """Example: 'me+reader1@gmail.com' -> 'me@gmail.com'"""
        return re.sub(r"\+.*(?=@)", "", email)

    def send_magic_link(self, email: str, token: str, expires_in: str):
        link = api_url_builder.build(path="auth/verify", query={"token": token})
        html_content = self.__render_template(
            "magic_link.html", link=link, expires_in=expires_in
        )
        subject = f"Login Link for {email}"  # include original email to distinguish
        resend.Emails.send(
            {
                "from": settings.FROM_EMAIL,
                "to": self.__normalize_for_delivery(email),
                "subject": subject,
                "html": html_content,
            }
        )

    def bulk_send_article_notifications(
        self,
        emails: list[str],
        notification_ids: list[int],
        article: Article,
        batch_size: int = settings.MAX_RECIPIENTS,
    ):
        if not emails or not article.is_published:
            return

        article_teaser = article.content[: min(len(article.content) // 5, 300)] + "..."
        article_url = fe_url_builder.build(f"/articles/{article.slug}")
        html_content = self.__render_template(
            "article_published.html",
            article_teaser=article_teaser,
            article_url=article_url,
        )
        subject = article.title

        for i in range(0, len(emails), batch_size):
            batch = emails[i : i + batch_size]

            # Idempotency key to avoid resending emails
            # (emails have been sent but haven't update statuses in DB)
            batch_last_notification_id = notification_ids[i + len(batch) - 1]
            idempotency_key = f"article_{article.id}-last_notification_{batch_last_notification_id}"

            resend.Batch.send(
                params=[
                    {
                        "from": settings.FROM_EMAIL,
                        "to": self.__normalize_for_delivery(email),
                        "subject": subject,
                        "html": html_content,
                    }
                    for email in batch
                ],
                options={"idempotency_key": idempotency_key},
            )
