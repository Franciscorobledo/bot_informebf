# AI Appointment Booking Bots (SaaS MVP)

## 1. High-level architecture (multi-tenant, config-first)

**Why FastAPI?** For this MVP I chose **Python + FastAPI** because it is lightweight, fast to iterate, has excellent type hints + Pydantic validation for structured JSON, and fits well with background webhooks and integrations (Slack/OpenAI/Google). It also deploys cleanly on Render with Uvicorn/Gunicorn. The architecture is designed so we can later swap or scale individual components without changing bot configurations.

**Core services**
- **Webhook API (FastAPI)**: Receives Slack events and orchestrates the booking flow.
- **Config Store (PostgreSQL)**: Stores tenants, bots, and rules. Bots are configured, not coded.
- **Conversation State Store**: Tracks in-progress booking sessions for each user per bot.
- **Integrations**:
  - **OpenAI**: intent + entity extraction only.
  - **Google Calendar**: availability + booking creation.
  - **Slack**: inbound events + outbound messages.

**Multi-tenant request flow**
1. Slack event hits `/webhooks/slack`.
2. Identify bot by `team_id + channel_id`.
3. Load bot config + feature flags from DB.
4. Use OpenAI to parse intent/entities (structured JSON).
5. Deterministic state machine decides next question or action.
6. Check availability via Google Calendar API.
7. Create event, confirm in Slack.

## 2. Database schema (tables + fields)

See `db/schema.sql` for full DDL. Highlights:

- **tenants**
  - `id`, `name`, `status`, `created_at`
- **bots**
  - `id`, `tenant_id`, `name`, `system_prompt`, `features`, `slack_team_id`, `slack_channel_id`, `google_calendar_id`
- **bot_rules**
  - `id`, `bot_id`, `rule_type`, `rule_payload`
- **conversation_sessions**
  - `id`, `bot_id`, `slack_user_id`, `state`, `context_json`, `updated_at`
- **appointments**
  - `id`, `bot_id`, `slack_user_id`, `service`, `start_time`, `end_time`, `google_event_id`
- **integrations**
  - `id`, `tenant_id`, `provider`, `access_token`, `refresh_token`, `expires_at`

## 3. API design (main endpoints)

**Public**
- `POST /webhooks/slack` — Slack event intake (multi-tenant).

**Internal / Admin (future)**
- `POST /tenants`
- `POST /bots`
- `PATCH /bots/{id}`
- `GET /bots/{id}/rules`

## 4. Slack webhook handler

Implemented in `app/main.py` with Slack event verification, bot resolution, state machine, and reply messages.

## 5. OpenAI intent extraction

Implemented in `app/services/openai_intent.py` with a strict JSON schema prompt. Example prompt + response are included in that module.

## 6. Appointment booking state machine

Implemented in `app/services/booking_state.py` as deterministic transitions based on extracted intent/entities. Steps:
- `START` → ask if user wants to book
- `ASK_SERVICE` → ask for service
- `ASK_DATE` → ask for date
- `ASK_TIME` → ask for time
- `CHECK_AVAILABILITY` → validate, then book
- `CONFIRMED`

## 7. Google Calendar integration example

Implemented in `app/services/google_calendar.py` with a minimal HTTP-based event creation example.

## 8. SaaS core vs bot configuration separation

**SaaS Core** (shared by all tenants): webhook handler, state machine, scheduling logic, integrations.
**Bot Configuration** (per tenant): prompt, features, Slack channel binding, calendar mapping, business rules.

---

### Quick start (local)
1. `pip install -r requirements.txt`
2. `uvicorn app.main:app --reload`

