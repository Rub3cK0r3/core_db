# 09-execution.md

Repo folder structure:

```
sentinel-db/
├─ collector/
│  ├─ main.py
│  └─ Dockerfile
├─ processor/
│  ├─ process.py
│  └─ Dockerfile
├─ db/
│  └─ docker-entrypoint-initdb.d/
├─ alert_engine/
│  ├─ alert.py
│  └─ Dockerfile
├─ logs/
└─ docker-compose.yml
```

Tmux layout:

* Pane 1: collector logs
* Pane 2: processor logs
* Pane 3: alert engine logs
* Pane 4: DB CLI (psql)

Deployment commands:

```bash
docker-compose up -d
docker-compose logs -f
systemctl start sentinel-db.service
```

CI/CD example: GitHub Actions runs `pytest` and builds Docker images, deploys to staging server via SSH.
