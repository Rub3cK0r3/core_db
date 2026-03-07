## core_db – Sentinel-style backend monitoring

`core_db` is a **backend-first, CLI-first event monitoring stack**.  
It ingests backend events, stores them in PostgreSQL, applies RBAC on the API, and generates alerts for critical events – all designed to run on a Linux server with Docker and terminal tooling only.

The codebase you are in is the **MVP implementation** of that idea.

### Features

- **FastAPI backend** with JWT auth and RBAC on all event endpoints
- **PostgreSQL** storage for events and alerts (ACID, queryable, index-heavy)
- **Audit-style logging** for logins and event access (visible via `docker compose logs`)
- **Alert persistence** for `error` / `fatal` events into a dedicated `alerts` table
- **Async infrastructure** (`AsyncManager`, async collector skeleton) ready for scale-out
- **Docker Compose** deployment, no frontend, everything driven via `curl`, `psql`, and logs

---

### Project layout (MVP)

```text
core_db/
├─ deploy/
│  ├─ compose.yml                 # Docker Compose stack (db + backend + workers)
│  ├─ docker/                     # Service Dockerfiles
│  └─ requirements.txt            # Runtime deps for containers
├─ db/
│  └─ init-scripts/
│     └─ V1_schema_dev.sql        # Roles, events/alerts tables, seed data
├─ src/
│  └─ core/
│     ├─ backend/                 # FastAPI app + ORM models
│     ├─ async_lib/               # AsyncManager + collector/processor/alert skeletons
│     ├─ db/                      # Low-level DB connection helper
│     └─ logs/                    # Logger + observer utilities
├─ docs/
│  └─ plan/                       # 00–11 design docs (this repo’s plan)
└─ README.md
```

---

### Running the stack (Docker / CLI-only)

Prerequisites: Docker, Docker Compose v2 (`docker compose`), and `psql`.

```bash
git clone <this-repo-url>
cd core_db

# Start from the deployment folder
cd deploy
docker compose up -d

# Follow logs from the backend (and others if you like)
docker compose logs -f backend
```

> If port `5432` is already in use on your host, adjust the `db` port mapping in `deploy/compose.yml` (for example `55432:5432`) and connect psql to that host port.

---

### CLI usage – minimal MVP flow

1. **Get a token**

   Insert at least one user in the `users` table (username + bcrypt-hashed password), then:

   ```bash
   curl -X POST "http://localhost:8000/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=alice&password=changeme"
   ```

   This returns a JSON with `access_token`.

2. **Create an event (also creates an alert for error/fatal)**

   ```bash
   TOKEN=...   # paste from previous response

   curl -X POST "http://localhost:8000/v1/events" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "id": "evt-1000",
          "severity": "error",
          "stack": "ExampleError: something broke",
          "type": "ExampleError",
          "timestamp": 1700000000000,
          "resource": "/api/test",
          "referrer": "https://example.com",
          "app_name": "SentinelDB Test",
          "app_version": "1.0.0",
          "app_stage": "testing",
          "tags": {"env": "dev"},
          "endpoint_id": "ep-1",
          "endpoint_language": "en-US",
          "endpoint_platform": "Linux x86_64",
          "endpoint_os": "Ubuntu",
          "endpoint_os_version": "22.04",
          "endpoint_runtime": "Python",
          "endpoint_runtime_version": "3.12",
          "endpoint_country": "US",
          "endpoint_user_agent": "curl/8.0",
          "endpoint_device_type": "Server"
        }'
   ```

3. **Inspect events and alerts via `psql`**

   ```bash
   psql "postgresql://devuser:devpass@localhost:5432/coredb"

   SELECT * FROM events ORDER BY received_at DESC LIMIT 5;
   SELECT * FROM alerts ORDER BY created_at DESC LIMIT 5;
   ```

4. **Audit and security signals**

   - Check `docker compose logs backend` for:
     - `AUTH_FAIL` / `AUTH_SUCCESS` lines
     - `LIST_EVENTS`, `GET_EVENT`, `CREATE_EVENT` audit entries

---

### Documentation

Design and planning docs live in `docs/plan/`:

- `00-personal-context.md` – environment and constraints
- `01-project-definition.md` – problem, personas, business framing
- `02-definition-of-done.md` – acceptance, operational, and security criteria
- `04-architecture.md` – high-level architecture diagram
- `06-concept-map.md` – subject areas to deepen
- `07-roadmap.md` – Level 0–3 roadmap (It Runs → Hardening)
- `11-examples-and-testcases.md` – CLI examples and test cases (MVP-focused)

Use those files as the living spec for evolving this repo from MVP into a hardened, attackable Sentinel-style platform.
=======
# core_db

![Python](https://img.shields.io/badge/python-3.11-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-in%20development-orange)

> Sistema CLI-first para ingesta, procesamiento y alertas de eventos backend, con enfoque en seguridad y auditabilidad.

`core_db` es un **framework backend-first** para manejar **event-pipelines** en Python. Permite recolectar eventos de sistemas empresariales, procesarlos de forma asincrónica, almacenar logs seguros y generar alertas, todo completamente desde la terminal. Está pensado para ser seguro, desplegable en Docker, y con trazabilidad total para auditoría.

---

## 🔹 Características principales

- Ingesta de eventos asincrónica confiable
- Normalización y procesamiento de eventos
- Almacenamiento seguro en PostgreSQL
- Motor de alertas configurable (CLI, email simulado, hooks a SIEM)
- Logs **tamper-evident**
- RBAC en todos los endpoints
- Deployable en Docker Compose y Kubernetes opcional
- Foco en seguridad, pentesting y hardening desde el primer día

---

## 📂 Estructura del proyecto

```

core_db/
├─ db/                # Scripts y utilidades de base de datos
├─ deploy/            # Configuraciones y scripts de despliegue
├─ docs/              # Documentación y ejemplos
├─ env/               # Entorno virtual y dependencias
├─ src/               # Código principal: AsyncManager, EventPipeline
├─ logs/              # Logs persistentes
└─ README.md

````

---

## ⚡ Instalación

```bash
git clone https://github.com/tu-usuario/core_db.git
cd core_db

# Crear entorno virtual
python -m venv env
source env/bin/activate   # Linux/macOS
env\Scripts\activate      # Windows

# Instalar dependencias
pip install -r requirements.txt

# Levantar stack básico (si ya tienes Docker Compose configurado)
docker-compose up -d
docker-compose logs -f
````

> Todo el sistema funciona **CLI-first**. No requiere frontend.

---

## 🚀 Uso básico

```python
from src.pipeline import AsyncManager

async_manager = AsyncManager()

# Registrar un evento
@async_manager.on_event("nuevo_registro")
async def handle_event(data):
    print(f"Evento recibido: {data}")

# Emitir un evento
async_manager.emit("nuevo_registro", {"id": 1, "user": "alice"})
```

> Para ejemplos completos, revisa `docs/examples.md`.

---

## 🛠️ Roadmap

**Level 0 — It Runs**

* Event Collector + DB Storage
* `docker-compose up` y prueba básica con `curl`

**Level 1 — MVP**

* Processor + Alert Engine
* RBAC y logs auditable

**Level 2 — Pro**

* Multi-container
* SIEM hooks
* Alta ingesta (>1000 eventos/min)

**Level 3 — Hardening & Pentesting**

* Unit/integration tests
* Fuzzing y ataques simulados
* Log tampering detection

---

## 🤝 Cómo colaborar

1. Haz un **fork** del proyecto
2. Crea branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am "Añadir nueva funcionalidad"`
4. Pull request
5. Usa **Issues** para bugs y propuestas

### Buenas prácticas

* Documenta cambios en `docs/`
* Mantén commits claros y atómicos
* Etiquetas sugeridas: `help wanted`, `good first issue`

---

## 🔒 Seguridad

* RBAC en todos los endpoints
* Logs **tamper-evident**
* Validación de inputs y protección contra inyecciones
* Anomaly detection para eventos sospechosos
* Pentesting de contenedores y autenticación

---

## 📝 Licencia

MIT License © 2026
