# Development

```bash
uv run uvicorn app.main:app --reload
```

# DB migration

[!!!] ALWAYS review _(and modify if needed)_ the generated script at `app/db/migration/versions/`.

```bash
# Generate migration script
uv run alembic revision --autogenerate -m "description"

# Apply
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```
