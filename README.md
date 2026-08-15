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
- Payment service provider: `Stripe`
- Email service: `Resend`

## Features

1. **Authentication & reader profile**

- [x] Login via email.
- [x] Connect Google account (reader only).
- [ ] Subscription & bought articles.
- [ ] Email preferences: opt-in or out of receiving emails.

2. **Payment & pay wall**

- [x] `Stripe` integration for checkout and billing management.
- [x] Paid content: show preview followed by call-to-action (CTA).

3. **Content & publishing**

- [x] Article creation & publishing.
- [ ] Article images and media.

4. **Email Delivery**

- [x] Send emails to subscribers when publishing articles.
- [ ] For admin: Email delivery statistics.

## UI/UX

- [ ] Responsive layout.
- [ ] Dark mode.

## Local development

See [DEVELOP.md](DEVELOP.md)
