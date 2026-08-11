.PHONY: dev stripe-dev

# Run server in development mode
dev:
	uv run uvicorn app.main:app --reload

# Forward (all) Stripe events to localhost
stripe-dev:
	stripe listen --forward-to http://localhost:8000/api/webhooks/stripe
