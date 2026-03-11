# 02-definition-of-done.md

Acceptable:

* [x] Backend collects events reliably (PostgreSQL + indexed schema)
* [x] RBAC enforced for all event endpoints (JWT bearer required)
* [x] Audit logs generated per action (auth + event access)
* [x] Alerts trigger on configurable thresholds (severity-based via `ALERT_MIN_SEVERITY`)
* [x] Deployable via Docker Compose
* [x] Runs entirely from CLI

Useless:

* [ ] No logging
* [ ] No security controls
* [ ] Only toy data, not deployable
* [ ] Requires frontend

Operational criteria:

* [ ] 99% uptime on local server
* [ ] Event ingestion <500ms (under defined load profile)
* [ ] Logs rotated and persisted (beyond container lifetime)

Security criteria:

* [x] Role-based access control (authenticated access to event API)
* [ ] Basic anomaly detection for database queries
* [ ] Alerts for suspicious activity (beyond severity-based alerts)
* [ ] Tamper-evident logs
