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
