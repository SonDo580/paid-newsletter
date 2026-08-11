from sqlmodel import Session, select

from app.db.connect import engine
from app.db.models.article import Article
from app.utils.datetime import datetime_utils


def _get_titles():
    return [
        "Understanding Stripe Webhook Integration",
        "Building Scalable Backend Systems with Python",
        "How Modern Paywalls Work: A Deep Dive into Subscriptions",
        "Mastering React Query and Optimistic UI Updates",
        "The Ultimate Guide to Async Database Operations in Python",
        "Designing Robust Authentication for SaaS Applications",
        "SQLite WAL Mode and Concurrency Performance Tips",
        "Building Production-Ready REST APIs with FastAPI",
        "Managing Subscription Life Cycles with Webhooks",
        "How to Write Clean, Testable Python Backend Code",
    ]


def _get_content() -> str:
    lorem_paragraph = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    target_len = 1000
    repeats = target_len // len(lorem_paragraph)
    return lorem_paragraph * repeats


def _generate_slug(title: str, index: int) -> str:
    clean = "".join(c.lower() if c.isalnum() or c.isspace() else "" for c in title)
    slug = "-".join(clean.split())
    return f"{slug}-{index}"


def seed_articles():
    now = datetime_utils.now_utc()
    content = _get_content()
    titles = _get_titles()
    print(f"Creating {len(titles)} articles...")

    with Session(engine) as db_session:
        created_count = 0

        for i, title in enumerate(titles):
            title = f"{titles[i]} #{i}"
            slug = _generate_slug(title, i)

            existing = db_session.exec(
                select(Article).where(Article.slug == slug)
            ).first()
            if existing:
                print(f"[Skipped] Slug '{slug}' already exists.")
                continue

            article = Article(
                title=title,
                slug=slug,
                content=content,
                is_free=False,
                is_published=True,
                published_at=now,
                created_at=now,
                updated_at=now,
            )
            db_session.add(article)
            created_count += 1

        db_session.commit()
        print(f"Successfully created {created_count} articles.")


if __name__ == "__main__":
    seed_articles()
