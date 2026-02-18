# 07-roadmap.md

Level 0 — It Runs

* [ ] Objective: Basic ingestion pipeline
* [ ] Deliverables: Event collector + DB
* [ ] Done: `docker-compose up`, test ingestion with `curl`

Level 1 — MVP

* [ ] Objective: RBAC, audit logs, basic alerts
* [ ] Deliverables: Processor + Alert Engine
* [ ] Done: Verify logs and alerts with sample events

Level 2 — Pro Version

* [ ] Objective: Advanced filtering, SIEM hooks, multi-container
* [ ] Deliverables: Full Docker Compose stack
* [ ] Done: Deploy, ingest >1000 events/min, alert triggers

Level 3 — Hardening & Pentesting

* [ ] Objective: Security review, penetration tests
* [ ] Deliverables: Unit tests, fuzz tests, log tampering detection
* [ ] Done: Execute test corpus, generate report
