## core_db – Sentinel-style backend monitoring

`core_db` is a **backend-first, CLI-first event monitoring stack**.  
It ingests backend events, stores them in PostgreSQL, applies RBAC on the API, and generates alerts for critical events – all designed to run on a Linux server with Docker and terminal tooling only.

The codebase you are in is the **MVP implementation** of that idea.

### Features

- **FastAPI backend** with JWT auth and RBAC on all event endpoints
- **PostgreSQL** storage for events and alerts (ACID, queryable, index-heavy)
- **Audit-style logging** for logins and event access (visible via `docker compose logs`)
- **Alert persistence** for `error` / `fatal` events into a dedicated `alerts` table
- **Async infrastructure** (`AsyncManager`, async collector skeleton) ready for scale-out
- **Docker Compose** deployment, no frontend, everything driven via `curl`, `psql`, and logs

---

### Project layout (MVP)

```text
core_db/
├─ deploy/
│  ├─ compose.yml                 # Docker Compose stack (db + backend + workers)
│  ├─ docker/                     # Service Dockerfiles
│  └─ requirements.txt            # Runtime deps for containers
├─ db/
│  └─ init-scripts/
│     └─ V1_schema_dev.sql        # Roles, events/alerts tables, seed data
├─ src/
│  └─ core/
│     ├─ backend/                 # FastAPI app + ORM models
│     ├─ async_lib/               # AsyncManager + collector/processor/alert skeletons
│     ├─ db/                      # Low-level DB connection helper
│     └─ logs/                    # Logger + observer utilities
├─ docs/
│  └─ plan/                       # 00–11 design docs (this repo’s plan)
└─ README.md
```

---

### Running the stack (Docker / CLI-only)

Prerequisites: Docker, Docker Compose v2 (`docker compose`), and `psql`.

```bash
git clone <this-repo-url>
cd core_db

# Start from the deployment folder
cd deploy
docker compose up -d

# Follow logs from the backend (and others if you like)
docker compose logs -f backend
```

> If port `5432` is already in use on your host, adjust the `db` port mapping in `deploy/compose.yml` (for example `55432:5432`) and connect psql to that host port.

---

### CLI usage – minimal MVP flow

1. **Get a token**

   Insert at least one user in the `users` table (username + bcrypt-hashed password), then:

   ```bash
   curl -X POST "http://localhost:8000/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=alice&password=changeme"
   ```

   This returns a JSON with `access_token`.

2. **Create an event (also creates an alert for error/fatal)**

   ```bash
   TOKEN=...   # paste from previous response

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

3. **Inspect events and alerts via `psql`**

   ```bash
   psql "postgresql://devuser:devpass@localhost:5432/coredb"

   SELECT * FROM events ORDER BY received_at DESC LIMIT 5;
   SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;
   ```

4. **Audit and security signals**

   - Check `docker compose logs backend` for:
     - `AUTH_FAIL` / `AUTH_SUCCESS` lines
     - `LIST_EVENTS`, `GET_EVENT`, `CREATE_EVENT` audit entries

---

### Documentation

Design and planning docs live in `docs/plan/`:

- `00-personal-context.md` – environment and constraints
- `01-project-definition.md` – problem, personas, business framing
- `02-definition-of-done.md` – acceptance, operational, and security criteria
- `04-architecture.md` – high-level architecture diagram
- `06-concept-map.md` – subject areas to deepen
- `07-roadmap.md` – Level 0–3 roadmap (It Runs → Hardening)
- `11-examples-and-testcases.md` – CLI examples and test cases (MVP-focused)

Use those files as the living spec for evolving this repo from MVP into a hardened, attackable Sentinel-style platform.
