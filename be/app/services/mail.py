import resend
from jinja2 import Environment, PackageLoader, select_autoescape
import re

from app.config.settings import settings
from app.utils.url import api_url_builder

jinja2_env = Environment(
    loader=PackageLoader("app", "templates/emails"),
    autoescape=select_autoescape(["html", "xml"]),
)


class MailService:
    def _render_template(self, template_name: str, **context) -> str:
        template = jinja2_env.get_template(template_name)
        return template.render(**context)

    def _normalize_for_delivery(self, email: str) -> str:
        """Example: 'me+reader1@gmail.com' -> 'me@gmail.com'"""
        return re.sub(r"\+.*(?=@)", "", email)

    def send(self, to_email: str, subject: str, html_content: str):
        resend.Emails.send(
            {
                "from": settings.FROM_EMAIL,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }
        )

    def send_magic_link(self, email: str, token: str, expires_in: str):
        link = api_url_builder.build(path="auth/verify", query={"token": token})
        html_content = self._render_template(
            "magic_link.html", link=link, expires_in=expires_in
        )
        delivery_email = self._normalize_for_delivery(email)
        subject = f"Login Link for {email}"  # include original email to distinguish
        self.send(to_email=delivery_email, subject=subject, html_content=html_content)
