# 06-concept-map.md

* [ ] Backend

  * Python backend service for event collection and processing
  * Central to ingest, normalize, and process enterprise events
  * search: "Python backend event processing enterprise"
  * resource: [https://docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/)

* [ ] Databases

  * PostgreSQL relational storage
  * Ensures auditability, ACID compliance, and complex queries
  * search: "PostgreSQL audit logging enterprise"
  * resource: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)

* [ ] Distributed Systems

  * Multi-container event pipeline (collector → processor → alert engine)
  * Supports scaling, isolation, and reliability
  * search: "docker compose multi-container architecture"
  * resource: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)

* [ ] Queues / Event Processing

  * Ingest events asynchronously, process, and trigger alerts
  * Necessary for real-time monitoring without blocking
  * search: "Python async event processing queue"
  * resource: [https://docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)

* [ ] Networking

  * TCP/UDP ingestion, inter-container networking, port exposure
  * Essential for detecting anomalous access
  * search: "docker container network security best practices"
  * resource: [https://docs.docker.com/network/](https://docs.docker.com/network/)

* [ ] Protocols

  * HTTP/HTTPS for REST ingestion
  * TLS for encryption in transit
  * search: "REST API secure TLS Python"
  * resource: [https://owasp.org/www-project-api-security/](https://owasp.org/www-project-api-security/)

* [ ] Security: RBAC

  * Role-based access control for every endpoint
  * Prevents unauthorized access to sensitive events
  * search: "Python FastAPI RBAC implementation"
  * resource: [https://owasp.org/www-community/controls/Role-Based_Access_Control](https://owasp.org/www-community/controls/Role-Based_Access_Control)

* [ ] Security: Anomaly Detection

  * Detect suspicious patterns in event payloads or frequency
  * Essential for insider threat detection
  * search: "Python anomaly detection real-time"
  * resource: [https://scikit-learn.org/stable/modules/outlier_detection.html](https://scikit-learn.org/stable/modules/outlier_detection.html)

* [ ] Security: Tamper-evident logs

  * Hash each log entry and chain to prevent manipulation
  * Important for compliance and audit
  * search: "tamper-evident logs python"
  * resource: [https://owasp.org/www-project-cheat-sheets/cheatsheets/Logging_Cheat_Sheet.html](https://owasp.org/www-project-cheat-sheets/cheatsheets/Logging_Cheat_Sheet.html)

* [ ] Security: Input Validation / Hardening

  * Sanitize all input (JSON, POST bodies, headers)
  * Prevent SQLi, injection, and malformed events
  * search: "Python input validation security"
  * resource: [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)

* [ ] Pentesting: SQLi / Injection

  * Test event ingestion for parameterized query enforcement
  * search: "PostgreSQL python parameterized queries"
  * resource: [https://portswigger.net/web-security/sql-injection](https://portswigger.net/web-security/sql-injection)

* [ ] Pentesting: Auth Bypass

  * Test RBAC misconfigurations, token replay
  * search: "JWT token attack bypass"
  * resource: [https://owasp.org/www-project-cheat-sheets/cheatsheets/JSON_Web_Token_Cheat_Sheet_for_Java.html](https://owasp.org/www-project-cheat-sheets/cheatsheets/JSON_Web_Token_Cheat_Sheet_for_Java.html)

* [ ] Pentesting: Container Security

  * Attempt escape, privilege escalation, network scanning
  * search: "docker container escape pentest"
  * resource: [https://docs.docker.com/engine/security/security/](https://docs.docker.com/engine/security/security/)

* [ ] Blue Team: Logs & Metrics

  * Centralize collector, processor, and alert engine logs
  * Monitor metrics for unusual patterns
  * search: "ELK stack docker monitoring"
  * resource: [https://www.elastic.co/what-is/elk-stack](https://www.elastic.co/what-is/elk-stack)

* [ ] Observability: Alerts

  * Configure thresholds for unusual event frequency
  * CLI alert messages + optional email/SIEM hooks
  * search: "Prometheus alerting docker"
  * resource: [https://prometheus.io/docs/alerting/latest/alertmanager/](https://prometheus.io/docs/alerting/latest/alertmanager/)

* [ ] SRE / Operations

  * Health checks, service restarts, log rotation
  * search: "docker healthcheck example"
  * resource: [https://docs.docker.com/engine/reference/builder/#healthcheck](https://docs.docker.com/engine/reference/builder/#healthcheck)

* [ ] DevOps / CI/CD

  * GitHub Actions build + test + deploy
  * Deploy Docker images to staging / production
  * search: "Python Docker CI/CD GitHub Actions"
  * resource: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

* [ ] Deployment

  * Docker Compose multi-container stack
  * Optional Kubernetes manifests for scaling
  * search: "docker compose production deploy"
  * resource: [https://docs.docker.com/compose/production/](https://docs.docker.com/compose/production/)

* [ ] Testing: Unit / Integration

  * Unit test backend functions
  * Integration test pipeline (collector → processor → DB → alert)
  * search: "pytest Docker integration testing"
  * resource: [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)

* [ ] Testing: Security / Fuzzing

  * Inject malformed events, attempt auth bypass, replay attacks
  * search: "Python fuzz testing REST API"
  * resource: [https://owasp.org/www-community/Fuzzing](https://owasp.org/www-community/Fuzzing)

* [ ] Performance / Load

  * Benchmark event throughput (>1000 events/min)
  * search: "Python event ingestion performance benchmark"
  * resource: [https://locust.io/docs/](https://locust.io/docs/)

* [ ] Cryptography

  * Hash logs, encrypt sensitive fields, TLS for transport
  * search: "Python cryptography library"
  * resource: [https://cryptography.io/en/latest/](https://cryptography.io/en/latest/)

* [ ] Authentication

  * JWT tokens, RBAC enforcement
  * MFA optional
  * search: "Python FastAPI JWT RBAC"
  * resource: [https://owasp.org/www-project-cheat-sheets/cheatsheets/JSON_Web_Token_Cheat_Sheet_for_Java.html](https://owasp.org/www-project-cheat-sheets/cheatsheets/JSON_Web_Token_Cheat_Sheet_for_Java.html)

* [ ] Hardening

  * Restrict container capabilities, read-only volumes
  * Harden PostgreSQL and OS
  * search: "docker container hardening CIS"
  * resource: [https://www.cisecurity.org/benchmark/docker/](https://www.cisecurity.org/benchmark/docker/)
