## Next steps to follow this proyect..

[  ] Fix the project structure
      -> Scalability, cleanliness, modularity

[  ] STEP 1 — Enforce Clean Architecture
      - [ ] Ensure strict layer separation:
            collector / queue / processor / db / domain
      - [ ] Remove circular imports and cross-layer coupling
      - [X] Database connection separated

[ X ] STEP 2 — Introduce Event Queue (Decoupling)
      - [ X ] Implement bounded thread-safe Event Queue
      - [ X ] Collector ONLY pushes to queue
      - [ X ] Processor ONLY consumes from queue
      - [ X ] Remove any direct Collector → DB interaction

[ X ] STEP 3 — Make Processor Thread-Safe
      - [ X ] Ensure safe DB usage per thread
      - [ X ] Remove shared mutable global state
      - [ X ] Verify no race conditions in processing logic

[ X ] STEP 4 — Implement Minimal Event Validation
      - [ X ] Define basic event schema (required fields only)
      - [ X ] Reject malformed events before DB write
      - [ X ] Print/log validation failures (prints acceptable)

[ X ] STEP 5 — Guarantee Deterministic DB Writes
      - [ X ] Use proper transactions
      - [ X ] Use parameterized queries
      - [ X ] Handle DB errors explicitly (no silent failures)

[ X ] STEP 6 — Add Graceful Shutdown Mechanism
      - [ X ] Stop accepting new events
      - [ X ] Signal processor threads to stop
      - [ X ] Drain queue completely
      - [ X ] Finish processing remaining events
      - [ X ] Close DB connections cleanly
      - [ X ] Join all threads

[  ] STEP 7 — Load Simulation
      - [ ] Create mock event generator
      - [ ] Simulate burst load (1k–10k events)
      - [ ] Confirm:
            no deadlocks
            no memory explosion
            no data loss
            queue drains correctly

[  ] STEP 8 — Testing Baseline
      - [ ] Unit test queue behavior
      - [ ] Unit test processor logic
      - [ ] Add 1 integration test (Collector → Queue → Processor → DB)

[  ] STEP 9 — Minimal Container Deployment
      - [ ] Create Docker Compose (collector + processor + postgres)
      - [ ] Validate full pipeline works inside containers

[  ] AFTER CORE IS STABLE (NOT NOW)
      - [ ] Observer pattern + modular handlers
      - [ ] Structured logging system
      - [ ] Alerting handlers
      - [ ] Metrics collection
      - [ ] Tamper-evident logs
      - [ ] Security / fuzz tests
      - [ ] Kubernetes manifests

```
                         +----------------+
                         | Enterprise App |  <-- Input events (REST/gRPC/CLI)
                         +--------+-------+
                                  |
                                  v
                           +--------------+
                           | Event Collector |  <-- Observer Pattern: publishes events
                           +------+---------+
                                  |
                                  v
                      +-----------+-----------+
                      | Event Queue (Threaded) |
                      +-----------+-----------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
        v                         v                         v
+----------------+       +----------------+       +----------------+
| Event Processor|       | Metrics Engine |       | Logger / Audit |
| (Threads)      |       | (Prometheus)   |       | (Tamper-evident|
| Validation &   |       | Counters,      |       |  Logs, CLI)    |
| Normalization  |       | Throughput,    |       |                |
+-------+--------+       | Error rates    |       +--------+-------+
        |                +----------------+                |
        v                                                 |
+----------------+                                       |
| DB Storage      | <------------------------------------+
| (PostgreSQL)    |
| ACID, Audit     |
+--------+--------+
         |
         v
+----------------+
| Alert Engine   |  <-- Observer: reacts to specific events
| CLI, Email,    |
| SIEM Hooks     |
+----------------+

```
