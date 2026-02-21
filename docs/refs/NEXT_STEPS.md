## Next steps to follow this proyect..

[  ] Fix the proyect structure
            -> Scalability, cleaniness etc etc
            - [ X ] Separate the database connection and make it less hardcoded and clean.
            - [  ] Watch out how not to repeat so many times the requirements.txt and Dockerfiles (integrate later when everything is set up)
            - [ X ] Change the main loops by Threads not to block the main thread and make it more efficient and scalable
            - [   ] Include Observer and handlers for notifying modules and pro printing instead of normal prints
            - [   ] Include Queues to reducer the bottleneck as with Threads, they both go together
            - [ ] Include Queues to reduce the bottleneck; combined with Threads for parallel processing
            - [ ] Implement event validation (pydantic/SQLModel schemas) before processing
            - [ ] Add modular logging system (loguru/structlog) instead of print statements
            - [ ] Include Observer and handlers for notifying modules and professional printing instead of normal prints
            - [ ] Integrate alerting handlers: CLI, email, SIEM hooks
            - [ ] Add metrics collection (Prometheus or custom counters) for throughput, error rates, etc.
            - [ ] Ensure tamper-evident logs for auditability
            - [ ] Implement unit and integration tests for Collector → Processor → Handlers pipeline
            - [ ] Security/fuzz tests: malformed events, replay attacks, auth bypass attempts
            - [ ] Add graceful shutdown mechanism for threads and queues
            - [ ] Prepare multi-container Docker Compose deployment for all services (Collector, Processor, AlertManager, DB)
            - [ ] Optional: Prepare Kubernetes manifests for scalable deployment
