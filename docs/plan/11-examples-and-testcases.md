# 11-examples-and-testcases.md

This document turns the high-level plan into **concrete CLI-first flows** you can run against the current MVP.

It assumes:

- You can run Docker and `docker compose`.
- You have `psql` available.
- You are comfortable working entirely from tmux + neovim + shell.

---

## 1. Implementation step index (MVP)

Status of the original steps, mapped to this repo:

- [x] Setup DB (PostgreSQL container + `events` / `alerts` tables + seed data)
- [x] Build collector (async collector skeleton with `AsyncManager` and `DATABASE_URL`)
- [x] Build processor (async processor skeleton with DB pool)
- [x] Build alert engine (async alert manager skeleton with DB pool)
- [x] Configure Docker Compose (`deploy/compose.yml` + service Dockerfiles)
- [x] Deploy full stack (`docker compose up` from `deploy/`)
- [x] Generate sample events (via `curl` to backend API)
- [x] Observe logs and alerts (via `docker compose logs` + `psql`)
- [ ] Execute evil path attacks (SQLi, auth bypass, replay, container abuse)
- [ ] Run unit and integration tests (aligned to this layout)
- [ ] Run security fuzz tests
- [ ] Validate deployment and rollback (staging → prod)

The sections below give **reproducible commands** for the “done” items and a starting point for the remaining ones.

---

## 2. Level 0 / Level 1: smoke test of the pipeline

Goal: Prove that the stack can start, accept authenticated events, persist them, and generate alerts for critical severities.

### 2.1 Start the stack

```bash
cd /path/to/core_db
cd deploy

# If host port 5432 is free
docker compose up -d

# If not, edit compose.yml and change:
#   - "5432:5432"
# to, e.g.:
#   - "55432:5432"
```

Verify containers:

```bash
docker compose ps
docker compose logs -f backend
```

### 2.2 Create a user in the database

Open a psql session to the Postgres container (adjust host port if you changed it):

```bash
psql "postgresql://devuser:devpass@localhost:5432/coredb"
```

Inside `psql`, create a user for API access (you must pre-compute the bcrypt hash; this is an example placeholder):

```sql
INSERT INTO users (username, email, hashed_password)
VALUES (
  'alice',
  'alice@example.com',
  '$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'  -- bcrypt hash
);
```

You can generate a hash with `python` and `passlib` in a separate shell if needed.

### 2.3 Obtain a JWT access token

```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=alice&password=changeme"
```

Expected:

- HTTP 200 with JSON containing `access_token` and `token_type: "bearer"`.
- Backend logs show **either** `AUTH_FAIL` **or** `AUTH_SUCCESS username=alice`.

Extract the token:

```bash
TOKEN=... # paste from JSON
```

### 2.4 Create a critical event (should also create an alert)

```bash
curl -X POST "http://localhost:8000/v1/events" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "id": "evt-1000",
       "severity": "error",
       "stack": "ExampleError: something broke",
       "type": "ExampleError",
       "timestamp": 1700000000000,
       "resource": "/api/test",
       "referrer": "https://example.com",
       "app_name": "SentinelDB Test",
       "app_version": "1.0.0",
       "app_stage": "testing",
       "tags": {"env": "dev"},
       "endpoint_id": "ep-1",
       "endpoint_language": "en-US",
       "endpoint_platform": "Linux x86_64",
       "endpoint_os": "Ubuntu",
       "endpoint_os_version": "22.04",
       "endpoint_runtime": "Python",
       "endpoint_runtime_version": "3.12",
       "endpoint_country": "US",
       "endpoint_user_agent": "curl/8.0",
       "endpoint_device_type": "Server"
     }'
```

Expected:

- HTTP 200 with the newly created event payload.
- Backend logs include a line like:
  - `CREATE_EVENT username=alice event_id=evt-1000 severity=error`

### 2.5 Verify persistence in DB

From `psql`:

```sql
SELECT id, severity, app_name, resource
FROM events
ORDER BY received_at DESC
LIMIT 5;

SELECT id, severity, resource
FROM alerts
ORDER BY created_at DESC
LIMIT 5;
```

Expected:

- `evt-1000` visible in `events`.
- An alert row with `id = 'evt-1000'` in `alerts` (because severity is `error`).

This closes the **Level 0 + Level 1 smoke test**.

---

## 3. Backend RBAC and audit log testcases

These focus on the FastAPI backend’s security behavior.

### 3.1 Unauthenticated access should fail

```bash
curl -i "http://localhost:8000/v1/events"
```

Expected:

- HTTP 401 with `{"detail":"Not authenticated"}` (FastAPI OAuth2 scheme).

### 3.2 Invalid token should be rejected and logged

```bash
curl -i "http://localhost:8000/v1/events" \
     -H "Authorization: Bearer invalid.token.here"
```

Expected:

- HTTP 401 with `{"detail":"Could not validate credentials"}`.
- Backend logs contain a 401 trace (JWT decode failure).

### 3.3 Wrong password should be logged as `AUTH_FAIL`

```bash
curl -i -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=alice&password=wrong"
```

Expected:

- HTTP 400 with `{"detail":"Incorrect username or password"}`.
- Backend logs contain: `AUTH_FAIL username=alice`.

### 3.4 Event read operations should be audited

```bash
# List events
curl -s "http://localhost:8000/v1/events" \
     -H "Authorization: Bearer $TOKEN" | jq length

# Fetch single event
curl -s "http://localhost:8000/v1/events/evt-1000" \
     -H "Authorization: Bearer $TOKEN"
```

Expected audit lines in logs:

- `LIST_EVENTS username=alice count=<N>`
- `GET_EVENT username=alice event_id=evt-1000`

---

## 4. Async collector / NOTIFY integration testcase (optional)

The `AsyncCollector` in `core.async_lib.collector.main` is designed to:

- Listen to a PostgreSQL `NOTIFY` channel (currently `events_channel`).
- Parse incoming JSON payloads as events.
- Insert them into the `events` table using an async pool.

This testcase assumes you run the collector service container from Compose.

### 4.1 Ensure collector is running

```bash
cd deploy
docker compose up -d collector
docker compose logs -f collector
```

You should see logs like:

- `DB pool created.`
- `AsyncCollector started.`

### 4.2 Emit a NOTIFY from psql

From `psql` connected to the same DB:

```sql
SELECT pg_notify(
  'events_channel',
  '{
     "type": "backend_error",
     "payload": {
       "id": "evt-notify-1",
       "app_name": "NotifyTest",
       "severity": "error"
     }
   }'
);
```

Expected:

- Collector logs show a processed event message.
- A corresponding row is inserted into `events` (depending on the collector’s mapping logic, which you can extend).

This is a good place to iterate on “in-band event ingestion” via Postgres.

---

## 5. Security / evil-path test ideas (to implement)

These are **not implemented yet**, but this repo is structured so you can add them:

1. **SQL injection simulation**
   - Craft malicious payloads and ensure all DB access still goes through ORM/parameterized APIs.

2. **Auth bypass attempts**
   - Replay tokens, use expired tokens, or tamper with JWT payloads; verify backend behavior and logs.

3. **Event replay**
   - Send the same critical event ID multiple times and define the desired semantics (idempotency vs duplicates).

4. **Log tampering**
   - Once tamper-evident logs are implemented, attempt to modify audit trails and verify the hash chain breaks.

5. **Container security**
   - Run basic recon tools from inside containers (where permitted) and harden Docker configuration to restrict capabilities.

You can track the implementation of each scenario as additional checkboxes in this file or in `08-security-red-vs-blue.md`.

---

## 6. Next steps

- Align `pytest` tests to the current `src/core/...` layout and run them in CI.
- Add log hashing / chaining for a minimal tamper-evident audit trail.
- Introduce basic anomaly detection (even simple thresholds) and wire alerts to those signals instead of just severity.
