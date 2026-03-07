# 09-execution.md

Repo folder structure (current MVP):

```text
core_db/
├─ deploy/
│  ├─ compose.yml
│  ├─ docker/
│  │  ├─ Backend.Dockerfile
│  │  ├─ Collector.Dockerfile
│  │  ├─ Processor.Dockerfile
│  │  └─ AlertEngine.Dockerfile
│  └─ requirements.txt
├─ db/
│  └─ init-scripts/
│     └─ V1_schema_dev.sql
├─ src/
│  └─ core/
│     ├─ backend/          # FastAPI app + SQLAlchemy models
│     ├─ async_lib/        # AsyncManager + collector/processor/alert skeleton
│     ├─ db/               # psycopg-based connection helper
│     └─ logs/             # Logger + observer utilities
├─ docs/
│  └─ plan/                # 00–11 design docs
└─ README.md
```

Tmux layout (suggested):

* Pane 1: `cd deploy && docker compose logs -f backend`
* Pane 2: `cd deploy && docker compose logs -f collector`
* Pane 3: `cd deploy && docker compose logs -f processor alert_engine`
* Pane 4: `psql "postgresql://devuser:devpass@localhost:5432/coredb"` (or the host port you mapped)

Deployment commands (local server):

```bash
cd /path/to/core_db
cd deploy

# Start services
docker compose up -d

# Follow logs
docker compose logs -f
```

CI/CD sketch (GitHub Actions):

* Job 1: run `pytest` (once tests are wired to this layout).
* Job 2: build images with `docker build` using the `deploy/docker/*.Dockerfile`.
* Job 3: push to registry and deploy to a staging server over SSH by running the same `docker compose up -d` from the `deploy` folder.
