# 08-security-red-vs-blue.md

Threat model:

* Insider injects malicious queries
* Rogue container exfiltrates data
* Auth bypass via API misuse
* Replay attacks on event ingestion
* Log tampering

Attacks:

* [ ] SQL injection simulation
* [ ] API key brute force
* [ ] Event replay
* [ ] Unauthorized access to logs
* [ ] Container escape attempt

Detection:

* [ ] Logs show failed auth attempts
* [ ] Alerts for abnormal DB queries
* [ ] Container metrics anomalies
* [ ] Audit log hashes mismatch

Mitigation:

* [ ] Parameterized queries
* [ ] Rate limiting
* [ ] RBAC enforcement
* [ ] Container namespace isolation
