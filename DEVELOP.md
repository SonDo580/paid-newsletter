# Prerequisites

- Python 3.13+ and `uv`
- Nodejs 22+ and `npm`
- Docker & Docker Compose
- Stripe CLI

# Frontend setup

```bash
cd fe

# Install dependencies
npm i

# Start dev server
npm run dev
```

# Service accounts setup

## `Resend`

- Create free account, create API key, update `.env`.
- **Gotcha**: In test mode, you can only send to your registered email.
- **Workaround**: Use `+` aliases for testing _(you@you.com, you+admin@you.com, you+reader1@you.com, you+reader2@you.com,...)_

## `Google OAuth`

- Go to `Google Cloud Console` and create new project _(find detailed instructions yourself)_, update `.env`.
- **Gotcha**:
  - In test mode, you must register test users with actual email.
  - The current flow is non-admin users first login with email, connect Google account, then they can login with Google in subsequent times.
  - So if both `Resend` and `Google OAuth` are in test mode, only the actual email that you use to register `Resend` can be used.

## `Stripe`

- Create new account under your existing account to separate resources, create product for subscription, config webhook _(optional for local development)_, update `.env`.

# Backend setup

```bash
cd be

# Create virtual environment and install dependencies
uv sync
```

## Create `.env`

- See `.env.example`.
- Replace variables as needed.

## Run services

```bash
# Redis, Database,...
make docker

# Backend
make api

# Worker
make worker
```

## Run scripts

```bash
uv run -m <module_path>

# Example:
uv run -m app.scripts.seed
```

# Database migration

[!!!] ALWAYS review _(and modify if needed)_ the generated script at `app/db/migration/versions/`.

```bash
# Generate migration script (after modifying DB models)
uv run alembic revision --autogenerate -m "description"

# Apply pending migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1
```

# Stripe testing

## Forward events to `localhost`

- Option 1: Use **Stripe CLI**

```bash
# Install Stripe CLI globally
npm install -g @stripe/cli

# Authenticate (session valid for 90 days)
stripe login

# Forward events to local server
make stripe
# To specify events
stripe listen --events <comma-separated list> --forward-to <webhook url>

# Trigger test event
stripe trigger <event_type>
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_succeeded

# Resend a specific event
stripe events resend <event_id>
```

- Option 2: Use `ngrok` to expose local port and paste the HTTPS URL into Stripe webhook settings dashboard.

## Simulate payments

- Details: https://docs.stripe.com/testing
- Example test cards:

```bash
# Standard success
4242424242424242
5555555555554444
...

# Generic Refusal
4000000000000002
...

# Refusal after attachment (to test past due)
4000000000000341
```

## Simulate time travel

- Use Stripe `Test Clocks`.
