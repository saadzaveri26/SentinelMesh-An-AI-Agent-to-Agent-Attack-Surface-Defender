# Skill: Setup Infrastructure

## Note on this skill
The reference folder structure this project followed included a
`setup_auth_clerk.md` skill. SentinelMesh's Semester 7 scope has no
multi-user login requirement — it is a single-operator security console, not
a multi-tenant app — so that skill is replaced with infrastructure setup
instead. If a login screen is ever required later, prefer Firebase Auth over
Clerk provided Firebase/Firestore is already part of the stack at that
point; otherwise raise it as an open decision rather than assuming.

## When to use
Once, at project bootstrap, and again any time a new service is added to
the stack.

## Steps

1. **Kafka**
   - Run a single-node Kafka broker via Docker (Confluent's or Apache's
     official image — confirm the exact image tag currently pulls
     successfully rather than assuming one from memory).
   - Create two topics: `agent.outbound` and `agent.inbound`.

2. **PostgreSQL**
   - Run via Docker with a persistent named volume so data survives
     container restarts.
   - Set up Alembic (or confirm it is already configured) for schema
     migrations — no manual `ALTER TABLE` during development.

3. **FastAPI service**
   - One service, connecting to both Kafka (as consumer/producer) and
     PostgreSQL (via SQLAlchemy).
   - Add a `/health` endpoint before anything else — this is the first thing
     to verify once Docker Compose is up.

4. **Next.js dashboard**
   - Separate service/container, talking to FastAPI over HTTP only — never
     connect directly to Kafka or PostgreSQL from the frontend.

5. **Docker Compose**
   - One `docker-compose.yml` bringing up Kafka, PostgreSQL, FastAPI, and
     Next.js together with a single command.
   - All secrets (DB credentials, any API keys) via a `.env` file, which
     must be in `.gitignore` — verify it actually is, don't assume.

6. **Verification before moving on**
   - `docker compose up` succeeds with no errors.
   - `/health` on the FastAPI service returns 200.
   - A test message published to `agent.outbound` is observable by a
     consumer — confirms the interception layer's plumbing works before any
     detection logic is built on top of it.
