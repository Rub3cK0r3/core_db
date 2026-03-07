# 07-roadmap.md

Level 0 — It Runs

* [x] Objective: Basic ingestion pipeline
* [x] Deliverables: Event collector + DB (containerized Postgres + events table)
* [x] Done: `docker compose up`, test ingestion with `curl`

Level 1 — MVP

* [x] Objective: RBAC, audit logs, basic alerts
* [x] Deliverables: Backend API + alert persistence on critical events
* [x] Done: Verify logs and alerts with sample events (see `11-examples-and-testcases.md`)

Level 2 — Pro Version

* [ ] Objective: Advanced filtering, SIEM hooks, multi-container
* [ ] Deliverables: Full Docker Compose stack
* [ ] Done: Deploy, ingest >1000 events/min, alert triggers

Level 3 — Hardening & Pentesting

* [ ] Objective: Security review, penetration tests
* [ ] Deliverables: Unit tests, fuzz tests, log tampering detection
* [ ] Done: Execute test corpus, generate report
