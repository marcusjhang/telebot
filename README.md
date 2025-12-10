# Telegram Water/Carb/Exercise Tracker – Delivery Plan

## Objectives
- Track per-user daily water goal (bottles), daily carb cap (portions; snack=1 portion, meal=2 portions), weekly exercise goal (sessions).
- Simple Telegram UX: buttons to add/decrease water, carbs, exercise; ask for quantity (and meal vs snack for carbs); broadcast update to all users.
- Auto-reset daily counters (and weekly exercise) while retaining history for weekly/monthly summaries.
- Web app to configure goals, view monthly progress, and edit limits.
- Cover end-to-end journeys: onboarding, goal setup, daily logging (+/−), progress viewing, notifications, resets, error handling, and web administration.

## User Journeys (Telegram)
- **New user onboarding**
  - `/start` greets, captures Telegram id/name, automatically sets timezone to Singapore Time (Asia/Singapore), sets safe defaults (e.g., 3 bottles, carb cap 4 portions, 6 weekly sessions).
  - Offers “Open Web App” (deep link) to customize goals; also offers quick inline goal edit for fast start.
  - Confirms registration and shows action menu (Water/Carb/Exercise/Progress/Settings).
- **Configure goals (bot quick edit)**
  - From `Settings` -> “Edit goals” -> inline buttons for each metric with current value; prompts for new numbers (validate >0, max guardrails).
  - Persist goals with `effective_from = today`.
- **Log water**
  - Tap `Water` -> prompt “Add or Decrease?” with +1/+2/+3 quick buttons and “Custom number”.
  - Accepts integer; clamps to zero on decrease; replies with updated total vs goal and remaining/overage.
  - Broadcast concise update to all users (respect opt-out).
- **Log carbs (portions)**
  - Tap `Carb` -> choose `Meal` (2 portions) or `Snack` (1 portion) -> choose Add/Decrease.
  - Quick buttons: +0.5, +1, +1.5, +2 portions (and matching negatives); allow custom entry in 0.5 increments.
  - Convert to portions, update daily carb total; show remaining under cap; warn on exceed with emoji.
  - Broadcast concise update.
- **Log exercise**
  - Tap `Exercise` -> choose Add/Decrease sessions -> quick +1 or custom number.
  - Exercise tracked against weekly goal but displayed in daily summary; do not allow negative weekly total.
  - Broadcast concise update.
- **View progress**
  - Tap `Progress` -> inline options: `Today`, `Past 7 days`, `This week exercise`, `Monthly summary (link to web)`.
  - Today: show water/carb per day vs goals and exercise progress; show streaks.
  - Past 7 days: per-day hit/miss icons, total overages.
- **Daily reset behavior**
  - At local midnight, daily counters roll over; user receives recap (if opted-in) and new day starts at zero.
  - Weekly exercise resets on configured week start (default Monday) with recap.
- **Error and edge handling**
  - Invalid input: prompt with validation message and show examples.
  - Race conditions/double taps: idempotency tokens on callback queries; discard duplicates.
  - Network/API down: apologize, retry, or queue; ensure no duplicate increments.
  - Spam guard: per-user rate limiting; broadcast throttling.

## User Journeys (Web App)
- **Auth and account linking**
  - Telegram Login Widget; backend verifies hash and issues JWT tied to telegram_user_id.
- **Edit goals**
  - Forms for water bottles/day, carb portions/day (helper copy: meal=2 portions, snack=1 portion), exercise sessions/week; inline validation and preview of impact.
  - Save -> backend writes new `goals` row with effective_from; show confirmation toast.
- **View dashboards**
  - Today card with remaining counts; weekly exercise meter; past 7-day table.
  - Monthly report: days hit/missed per metric, averages, overage counts, streaks; export CSV.
- **Notification preferences**
  - Toggle broadcast opt-out, recap delivery, timezone change.
- **Account maintenance**
  - Delete account/data; log out; see device/session info (optional).

## Architecture
- **Services**: (1) Telegram Bot service, (2) Backend API, (3) Web app, (4) DB, (5) Scheduler/worker.
- **Bot**: Telegraf (Node) or python-telegram-bot; uses backend API for persistence. Inline keyboards for +/− flows and progress quick view.
- **Backend**: REST/GraphQL with auth tokens per bot; handles business rules, aggregates, history, notifications fan-out.
- **Web app**: SPA (Next.js/React or Vue) consuming same API.
- **DB**: Postgres (row-level timezones/UTC timestamps). Tables for users, goals, daily_logs, weekly_logs, notifications, audit.
- **Events/Queue**: Optional lightweight queue (BullMQ/Sidekiq/Celery) for broadcast notifications to avoid blocking bot replies.
- **Config/Secrets**: Bot token, webhook URL, DB URL stored in env/secret manager.

## Data Model (sketch)
- `users`: telegram_user_id (PK), username, tz (default: 'Asia/Singapore'), created_at, last_active.
- `goals`: user_id, daily_water_bottles, daily_carb_max_portions, weekly_exercise_sessions, effective_from.
- `daily_logs`: id, user_id, date_utc, water_bottles, carb_portions, exercise_sessions, updated_at.
- `weekly_logs`: id, user_id, week_start_date, exercise_sessions.
- `events`: id, user_id, type (water|carb|exercise), delta, delta_portions?, subtype (meal|snack|custom), occurred_at, message_id (for edits), source (bot/web).
- `notifications`: id, payload, audience (all users), status, sent_at.
- `monthly_stats` (materialized view/job): aggregates days hit/missed per metric.

## Logic Details
- **Goal resolution**: For each event, pick latest goal row effective <= now; cache per-user.
- **Daily aggregation**: Upserts into daily_logs; reject negative totals; clamp decreases to zero.
- **Weekly aggregation**: Upserts exercise into weekly_logs; resets on configured week start.
- **Streaks**: Derived from daily_logs against goals; store in monthly_stats for faster reads.
- **Timezone**: All users use Singapore Time (Asia/Singapore, UTC+8); midnight reset and recaps at Singapore midnight.
- **Carb portions**: Meal=2 portions; snack=1 portion; quick buttons use 0.5/1/1.5/2 portion deltas; custom entry accepts 0.5 steps; all stored as portions.
- **Idempotency**: Use callback query id/message id as key; drop duplicates; expose `Idempotency-Key` header in API.
- **Broadcast rules**: Fan-out via queue; skip opted-out users; collapse bursts (e.g., multiple updates within 1 minute) into a single summary.

## Telegram Bot Flows
- **Entry point**: `/start` -> register user, automatically set timezone to Singapore Time, prompt to open web app for goals or use defaults.
- **Action menu (persistent buttons)**: `Water`, `Carb`, `Exercise`, `Progress`.
- **Add/Decrease flow**:
  - Step 1: choose metric (water/carb/exercise).
  - Step 2: prompt for subtype + quantity:
    - Water: ask bottles (integer), show quick +1/+2 buttons, allow manual number entry. Provide decrease option.
    - Carb: choose `Meal` (2 portions) or `Snack` (1 portion); quick +0.5/+1/+1.5/+2 portion buttons (and negatives); allow manual portion entry in 0.5 steps.
    - Exercise: ask sessions to add/decrease for the day (or this week).
  - Validation: non-negative totals; clamp to zero; store event; update daily/weekly log.
- **Progress**:
  - Today view: show totals vs goals, remaining to hit/avoid, streak badge (days meeting goals).
  - Past week: list 7 days with emoji for hit/miss; include weekly exercise completion.
- **Notifications**:
  - After any update, broadcast concise message to all users (rate-limit to avoid spam; optionally allow users to opt-out in settings).
  - Daily recap at local midnight+5m: show daily totals and hit/miss; weekly recap on week end.
- **Resets**:
  - Daily job per timezone to reset water/carb/exercise day counts; weekly reset for exercise on chosen weekday; history kept via events/logs.

## State Machine per Interaction
- Each user interaction tracked via `session_state` in bot middleware: waiting_for_metric -> waiting_for_subtype (carb) -> waiting_for_action (add/decrease) -> waiting_for_quantity -> confirm -> complete.
- Time out idle conversations (e.g., 5 minutes) and cancel gracefully.
- Allow `Cancel` button at each step to return to main menu.

## Web App (Goals & Reports)
- Auth via Telegram Login Widget/JWT tied to telegram_user_id.
- Forms to edit daily water goal, carb cap in portions (meal=2, snack=1), weekly exercise goal; preview current goals and effective date.
- Dashboard cards: today’s progress, remaining vs goals, weekly exercise meter.
- Monthly report: number of days meeting goals, average bottles, carb overage count, exercise compliance; simple charts.
- Settings: notification opt-out, timezone change, broadcast preferences.

## APIs (examples)
- `POST /users` (idempotent create from /start) body `{tz?, username?}`
- `GET /me/goals`, `POST /me/goals` body `{daily_water_bottles, daily_carb_max_portions, weekly_exercise_sessions, effective_from?}`
- `POST /me/logs/{metric}` body `{delta, subtype?}` (handles add/decrease and clamps to >=0)
- `GET /me/progress/today`, `GET /me/progress/week`, `GET /me/progress/month`
- `POST /notifications/broadcast` (worker use)
- Headers: `Authorization: Bearer <bot-token or user JWT>`, optional `Idempotency-Key`.
- Errors standardized: 400 validation, 401 auth, 409 idempotent duplicate, 429 rate limited.

## Scheduler/Jobs
- Per-timezone daily reset worker to roll daily_logs and emit recaps.
- Weekly exercise reset (pick locale week start).
- Monthly stats refresh (materialized view or cached aggregates).
- Backfill/migration scripts for schema changes.

## Deployment Plan
- Containerize bot+backend; web app as static build behind CDN.
- Environments: dev, staging, prod; separate bot tokens/webhooks per env.
- Webhook vs long-polling: prefer webhook (behind HTTPS, e.g., Fly.io/Render/Heroku/Cloud Run) with a small healthcheck endpoint.
- DB: managed Postgres (supabase/railway/neon/RDS); run migrations via CI.
- Secrets: stored in platform secrets manager; rotate periodically.
- Monitoring: basic logs, error reporting (Sentry), uptime pings on webhook and cron workers.

## Testing & QA
- Unit: command handlers, validation, goal calculations, reset logic.
- Integration: end-to-end bot conversation scripts (happy + edge: negative delta, large inputs).
- Load: broadcast notifications fan-out under small user set to ensure queue works.
- Web: form validation, auth flow, timezone changes; visual smoke on staging.

## Minimal Extra Features to Cover Gaps
- All users use Singapore Time (Asia/Singapore) - no timezone selection needed.
- Allow users to opt-out of global broadcast or limit to group/channel to prevent spam.
- Idempotency keys for bot updates to avoid double counts on retries.
- Basic export (CSV of events) for users who want raw data.
- Admin flag to mute abusive users or purge data on request.

## Open Questions to Resolve Early
- Default goals per new user; should they be enforced or suggested?
- Broadcast scope: all users, or a channel/group only? Opt-in vs opt-out default?
- Weekly reset day configurable per user or global?
- Do decreases allow going below zero (currently clamped)?
- Should exercise be loggable per day or anytime against weekly bucket?
