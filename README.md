# Paid Newsletter

A self-hosted newsletter platform for independent publishers who want full control over their monetization.

- Support both subscriptions and per-article purchases.
- Only support self-publishing.

## Benefits, which are also Limitations :)

- You can modify source code as needed <-> You have to modify source code if needed _(for example: change UI, security updates)_
- You have full control over hosting <-> You have to manage server, backup database, ...

## Tech stack

- Backend: `FastAPI`
- Frontend: `ReactJS`
- Database: `SQLite`
- Payment: `Stripe`
- Email: `Resend`

## Features

1. **Authentication & reader profile**

- Password-less login via email.
- Subscription status & bought articles.
- Email preferences: a way for users to opt-in or out of receiving newsletter via email.

2. **Payment & pay wall**

- PSP (`Stripe`) integration for checkout.
- Paid content: show preview followed by call-to-action (CTA) to pay.
- For admin: set subscription fee and article global price.

3. **Admin Panel**

- Manage articles.
- Manage readers (subscribers, one-time buyers).

4. **Email Delivery**

- Send published articles to subscribers. Every email should have a `Read on website` link.
- For admin:
  - Email delivery statistics.
  - Resend failed batches.
