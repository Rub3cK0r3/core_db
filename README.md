# core_db – Sentinel-style Backend Monitoring

![Python](https://img.shields.io/badge/python-3.11+-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-in%20development-orange)

> CLI-first system for backend event ingestion, processing, and alerting with a focus on security and auditability.

`core_db` is a **backend-first framework** for handling **event-pipelines** in Python. It enables collecting events from enterprise systems, processing them asynchronously, storing secure logs, and generating alerts — all from the command line. Designed to be secure, deployable via Docker, with full traceability for auditing.

---

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

---

## ✨ Features

- **Asynchronous Event Ingestion** – Reliable async event collection
- **Event Normalization & Processing** – Transform and process events in real-time
- **Secure PostgreSQL Storage** – Tamper-evident logging with SQLAlchemy/SQLModel
- **Configurable Alert Engine** – CLI alerts, email simulation, SIEM hooks
- **RBAC on All Endpoints** – Role-based access control built-in
- **Docker & Kubernetes Ready** – Deploy with Docker Compose or K8s
- **Security-First Design** – Pentesting and hardening from day one

---

## 📋 Requirements

### System Requirements

- **Python**: 3.11 or higher
- **PostgreSQL**: 14 or higher (or use Docker)
- **Docker**: 20.10+ (optional, for containerized deployment)
- **Docker Compose**: 2.0+ (optional)

### Supported Platforms

- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS (12.0+)
- Windows 10/11 (with WSL2 recommended)

---

## 🚀 Installation

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/Rub3cK0r3/core_db.git
cd core_db

# Create virtual environment
python -m venv env

# Activate virtual environment
# Linux/macOS:
source env/bin/activate
# Windows:
env\Scripts\activate

# Install dependencies
pip install -r deploy/requirements.txt
```

### Option 2: Docker Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rub3cK0r3/core_db.git
cd core_db

# Start all services
cd deploy
docker-compose up -d

# View logs
docker-compose logs -f
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Test imports
python -c "from core.async_lib.async_manager import AsyncManager; print('✓ Import successful')"
```

---

## ⚡ Quick Start

### 1. Set Up Database (Local Installation)

```bash
# Create PostgreSQL database
createdb coredb

# Or use Docker
 docker run -d \
   --name core_db_postgres \
   -e POSTGRES_USER=devuser \
   -e POSTGRES_PASSWORD=devpass \
   -e POSTGRES_DB=coredb \
   -p 5432:5432 \
   postgres:16
```

### 2. Configure Environment

```bash
cd src

# Copy environment template (if available)
cp .env/.env.example .env/.env.local

# Edit configuration
export DATABASE_URL="postgresql://devuser:devpass@localhost:5432/coredb"
export SECRET_KEY="your-secret-key-here"
```

### 3. Run the Application

```bash
# Start the main application
cd src
python setup.py
```

---

## 📖 Usage Examples

### Basic Event Processing

```python
import asyncio
from core.async_lib.async_manager import AsyncManager

async def main():
    # Initialize async manager with 4 workers
    async_manager = AsyncManager(worker_count=4)
    
    # Define event handler
    async def handle_event(data):
        print(f"Processing event: {data}")
    
    # Start workers
    await async_manager.start(handle_event)
    
    # Enqueue events
    await async_manager.enqueue({"type": "user_login", "user_id": 123})
    await async_manager.enqueue({"type": "transaction", "amount": 99.99})
    
    # Graceful shutdown
    await asyncio.sleep(2)
    await async_manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Full Pipeline Setup

```python
import asyncio
from core.async_lib.collector.main import AsyncCollector
from core.async_lib.processor.main import EventProcessor
from core.async_lib.async_manager import AsyncManager
from core.backend.database import engine

async def start_services():
    # Initialize components
    processor = EventProcessor(engine)
    async_manager = AsyncManager(worker_count=4)
    
    # Start async manager with processor
    await async_manager.start(processor.handle)
    
    # Initialize collector
    collector = AsyncCollector(db_dsn=None, worker_count=4)
    collector.async_manager = async_manager
    collector.listener_task = asyncio.create_task(collector._listener_loop())
    
    print("✓ All services started. Running forever...")
    
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        print("Stopping services...")
        collector.listener_task.cancel()
        try:
            await collector.listener_task
        except asyncio.CancelledError:
            pass
        await async_manager.stop()

def run_app():
    asyncio.run(start_services())

if __name__ == "__main__":
    run_app()
```

### Docker Compose Usage

```bash
# Start all services
cd deploy
docker-compose up -d

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f collector

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## 📂 Project Structure

```
core_db/
├── src/                    # Main source code
│   ├── core/              # Core application modules
│   │   ├── async_lib/     # Async processing library
│   │   │   ├── async_manager.py    # Task queue manager
│   │   │   ├── collector/          # Event collector
│   │   │   ├── processor/          # Event processor
│   │   │   └── alert_engine/       # Alert system
│   │   ├── backend/       # Backend API and database
│   │   ├── db/            # Database models and migrations
│   │   └── logs/          # Logging utilities
│   ├── setup.py           # Application entry point
│   └── .env/              # Environment and dependencies
├── deploy/                # Deployment configurations
│   ├── compose.yml        # Docker Compose setup
│   ├── docker/            # Dockerfiles for services
│   └── requirements.txt   # Python dependencies
├── db/                    # Database scripts and migrations
├── docs/                  # Documentation
│   ├── plan/              # Project planning documents
│   └── refs/              # Reference materials
├── tests/                 # Test suite
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # MIT License
└── README.md              # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://devuser:devpass@db:5432/coredb` |
| `SECRET_KEY` | Secret key for encryption | `dev-secret-key` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `WORKER_COUNT` | Number of async workers | `4` |
| `MAX_QUEUE_SIZE` | Maximum event queue size | `1000` |

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `db` | 5432 | PostgreSQL database |
| `backend` | 8000 | Main backend API |
| `collector` | 8001 | Event collector service |
| `processor` | 8002 | Event processor service |
| `alert_engine` | 8003 | Alert engine service |

---

## 🤝 Contributing

We welcome contributions of any kind: code, documentation, tests, or ideas! 💜

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/core_db.git
   cd core_db
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and commit:
   ```bash
   git commit -am "Add: your feature description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on GitHub

### Development Guidelines

- Follow **PEP 8** style guide for Python code
- Write clear, atomic commits with descriptive messages
- Add tests for new functionality
- Update documentation for API changes
- Reference related issues in PRs (`Closes #123`)

### Running Tests

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=src

# Run integration tests (requires Docker)
docker-compose -f deploy/compose.yml up -d
pytest tests/integration/
```

### Reporting Issues

- Use **GitHub Issues** for bug reports and feature requests
- Provide clear reproduction steps for bugs
- Include relevant logs and screenshots
- Look for `good first issue` or `help wanted` labels to get started

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## 🔒 Security

Security is a core focus of `core_db`:

- **RBAC** – Role-based access control on all endpoints
- **Tamper-Evident Logs** – Cryptographic integrity for audit logs
- **Input Validation** – Protection against injection attacks
- **Anomaly Detection** – Suspicious event pattern detection
- **Container Security** – Regular pentesting and hardening

### Reporting Security Issues

Please report security vulnerabilities privately via GitHub Security Advisories or email the maintainers directly. Do not open public issues for security bugs.

---

## 🗺️ Roadmap

### Level 0 — It Runs ✅
- Event Collector + DB Storage
- `docker-compose up` with basic `curl` testing

### Level 1 — MVP 🚧
- Processor + Alert Engine
- RBAC and auditable logs

### Level 2 — Pro 📋
- Multi-container orchestration
- SIEM hooks integration
- High ingestion rate (>1000 events/min)

### Level 3 — Hardening & Pentesting 📋
- Comprehensive unit/integration tests
- Fuzzing and simulated attacks
- Log tampering detection

---

## 📝 License

MIT License © 2026

See [LICENSE](LICENSE) for full text.

---

## 💬 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/Rub3cK0r3/core_db/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Rub3cK0r3/core_db/discussions)

---

<p align="center">
  Built with 🔒 security and ⚡ performance in mind.
</p>
