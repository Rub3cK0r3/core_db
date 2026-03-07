# 08-security-red-vs-blue.md

Threat model:

* Insider injects malicious queries
* Rogue container exfiltrates data
* Auth bypass via API misuse
* Replay attacks on event ingestion
* Log tampering

Attacks:

* [ ] SQL injection simulation
* [ ] API key / password brute force
* [ ] Event replay
* [ ] Unauthorized access to logs
* [ ] Container escape attempt

Detection:

* [x] Logs show failed auth attempts (e.g. `AUTH_FAIL` in backend logs)
* [ ] Alerts for abnormal DB queries
* [ ] Container metrics anomalies
* [ ] Audit log hashes mismatch

Mitigation:

* [x] Parameterized queries / ORM (SQLAlchemy + psycopg)
* [ ] Rate limiting
* [x] RBAC enforcement (JWT-required event API)
* [ ] Container namespace isolation / hardening
