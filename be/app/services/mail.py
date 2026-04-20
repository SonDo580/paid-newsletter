import resend
from jinja2 import Environment, PackageLoader, select_autoescape
import re

from app.config.settings import settings
from app.utils.url import api_url_builder

resend.api_key = settings.RESEND_API_KEY

jinja2_env = Environment(
    loader=PackageLoader("app", "templates/emails"),
    autoescape=select_autoescape(["html", "xml"]),
)


class MailService:
    @staticmethod
    def _render_template(template_name: str, **context) -> str:
        template = jinja2_env.get_template(template_name)
        return template.render(**context)

    @staticmethod
    def _normalize_for_delivery(email: str) -> str:
        """Example: 'me+reader1@gmail.com' -> 'me@gmail.com'"""
        return re.sub(r"\+.*(?=@)", "", email)

    @staticmethod
    def send(to_email: str, subject: str, html_content: str):
        resend.Emails.send(
            {
                "from": settings.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }
        )

    @staticmethod
    def send_magic_link(email: str, token: str, expires_in: str):
        link = api_url_builder.build(path="auth/verify", query={"token": token})
        html_content = MailService._render_template(
            "magic_link.html", link=link, expires_in=expires_in
        )
        delivery_email = MailService._normalize_for_delivery(email)
        subject = f"Login Link for {email}"  # include original email to distinguish
        MailService.send(
            to_email=delivery_email, subject=subject, html_content=html_content
        )
