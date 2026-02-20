# 00-personal-context.md

My goals are to build a serious, backend-first, infrastructure-heavy system that I can deploy on Linux servers using CLI tools. I prioritize backend engineering, security relevance, and operational realism. Frontend is irrelevant. I explicitly do not care about web UI or graphics.

Environment:

* Linux (CLI-first)
* ThinkPad
* Sway
* tmux
* neovim

Priorities:

* Backend robustness
* Database integrity
* Security from day one (defense-oriented)
* Deployable with Docker / Kubernetes
* Enterprise-oriented metrics

Constraints:

* Everything runs from the terminal
* Full logs and audit trails
* Deployable and attackable in real scenarios

---

# 01-project-definition.md

Project Name: SentinelDB

One-line pitch: Self-hosted enterprise backend monitoring and alert platform.

Problem it solves: Detects, logs, and alerts on anomalous backend events and suspicious database activity to reduce breach risk and meet compliance requirements.

Why it matters: Combines backend data collection, infrastructure observability, and security monitoring in a single CLI-first platform. Gives IT teams real-time insights into internal threats and operational anomalies.

Buyer personas:

* CISO
* IT Security Manager
* SOC Team
* Compliance Officer

Business driver: Prevents data breaches, insider threats, and compliance violations. Reduces MTTR for incidents, provides audit trails for regulations.

Commercial viability: Self-hosted license ($5k/year), managed service ($10–15k/year per instance), ROI via reduced breach cost and compliance penalties. Hooks for integration into SIEM and logging pipelines.

---

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

---

# 03-daily-tools.md

Tools I actually use:

* [ ] tmux for session management
* [ ] neovim for editing
* [ ] docker / docker-compose for containers
* [ ] bash scripts for automation
* [ ] PostgreSQL CLI (psql)
* [ ] curl / wget for requests
* [ ] git for version control
* [ ] tcpdump / nmap for network checks
* [ ] journalctl / systemctl for system monitoring

---

# 04-architecture.md

High-level description:

SentinelDB ingests backend events from enterprise apps, normalizes them, stores in a central DB, applies RBAC, and triggers alerts. It runs in containers orchestrated with Docker Compose, optionally deployable on Kubernetes.

ASCII diagram:

```
+----------------+        +----------------+
| Enterprise App | --->   | Event Collector|
+----------------+        +----------------+
                                 |
                                 v
                          +----------------+
                          | Event Processor|
                          +----------------+
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
             +------------+            +-------------+
             | DB Storage |            | Alert Engine|
             +------------+            +-------------+
                    |
                    v
             +----------------+
             | Audit & Logs   |
             +----------------+
```

Components:

* Event Collector: REST/gRPC ingestion
* Processor: Normalizes, filters, and enriches events
* DB Storage: PostgreSQL
* Alert Engine: Sends CLI alerts / emails / SIEM hooks
* Audit & Logs: Tamper-evident storage

Bottlenecks / SPOFs:

* DB overload → horizontal scaling
* Single collector → use multiple collectors in Compose

---

# 05-stack-decisions.md

Main stack:

* Python + FastAPI
* PostgreSQL
* Docker + Compose
* Bash for automation
* Nginx (optional, CLI logs only)

Alternative stacks:

* Go for high-performance backend
* Redis for ephemeral event queue

Tradeoffs:

* Python allows fast prototyping, large ecosystem
* PostgreSQL ensures relational integrity
* Docker ensures reproducible deployment
* Go/Redis optional if scaling needed

---

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

---

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

---

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

---

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

---

# 10-final-rules.md

Engineering principles:

* [ ] Everything observable
* [ ] CLI-first
* [ ] RBAC enforced
* [ ] Tamper-evident logs
* [ ] Incremental build
* [ ] Documented with examples
* [ ] Always reproducible in Docker
* [ ] Security from day one

---

# 11-examples-and-testcases.md

*(Aquí se integraría el contenido completo de ejemplos y testcases detallados que definimos anteriormente, con pasos de implementación, payloads, logs, tests, y comandos CLI. Además se podrían incluir los scripts Python y Dockerfiles comentados para copia directa.)*

