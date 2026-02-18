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
