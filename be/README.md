# Development guide

## Installation

```bash
uv sync

# add dependencies
uv add <package>
```

## Start server

```bash
make dev
```

## DB migration

[!!!] ALWAYS review _(and modify if needed)_ the generated script at `app/db/migration/versions/`.

```bash
# Generate migration script
uv run alembic revision --autogenerate -m "description"

# Apply
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## Run module

```bash
# Example
uv run -m app.scripts.seed
```

## Receive Stripe events on `localhost`

- Method 1: USe `Stripe CLI`

```bash
# Install CLI
npm install -g @stripe/cli

# Login (session valid for 90 days)
stripe login

# Listen and forward events to localhost
make stripe-dev
# (Optional) Only forward needed events
stripe listen --events <comma-separated list> --forward-to <webhook url>

# Send an event:
stripe trigger <event_type>
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_succeeded

# Resend specific event:
stripe events resend <event_id>
```

- Method 2: Use `ngrok`

## Simulate payments

- Details: https://docs.stripe.com/testing
- Example test cards:

```bash
4242424242424242
5555555555554444
...

# Refusal
4000000000000002
...

# Refusal after attachment (test past due)
4000000000000341
```
