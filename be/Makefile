# Commands for local development

.PHONY: docker api worker stripe

# Run services in Docker
docker: 
	docker compose up -d

# Run server
api:
	uv run uvicorn app.main:app --reload

# Run ARQ worker
worker:
	uv run arq app.worker.WorkerSettings

# Forward all Stripe events to localhost
stripe:
	stripe listen --forward-to http://localhost:8000/api/webhooks/stripe
