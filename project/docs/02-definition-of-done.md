# 02-definition-of-done.md

Acceptable:

* [ ] Backend collects events reliably
* [ ] RBAC enforced for all endpoints
* [ ] Audit logs generated per action
* [ ] Alerts trigger on configurable thresholds
* [ ] Deployable via Docker Compose
* [ ] Runs entirely from CLI

Useless:

* [ ] No logging
* [ ] No security controls
* [ ] Only toy data, not deployable
* [ ] Requires frontend

Operational criteria:

* [ ] 99% uptime on local server
* [ ] Event ingestion <500ms
* [ ] Logs rotated and persisted

Security criteria:

* [ ] Role-based access control
* [ ] Basic anomaly detection for database queries
* [ ] Alerts for suspicious activity
* [ ] Tamper-evident logs
