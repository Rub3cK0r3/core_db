# MVP Execution Guide — core_db  
# Guía de ejecución MVP — core_db

This document describes how to build, run, and verify **core_db** as a minimum viable product (MVP): a backend for event ingestion, processing, and alerting.  
Este documento describe cómo compilar, levantar y verificar el proyecto **core_db** como producto mínimo viable (MVP): backend para ingesta, procesado y alertas de eventos.

---

## [EN] English

### MVP status conclusions

After reviewing build, deployment, and automated tests, the project status is:

| Aspect | Status | Notes |
|--------|--------|--------|
| **Build and imports** | ✅ OK | With a virtualenv and `PYTHONPATH=src`, core modules (backend, async_lib, database) import without errors. |
| **Docker build** | ✅ OK | `docker compose build` in `deploy/` completes successfully for backend, collector, processor, and alert_engine. |
| **Docker run** | ⚠️ Environment-dependent | The stack requires port **5432** to be free. If PostgreSQL or another service is using it, `docker compose up -d` will fail until the port is freed or the mapping is changed. |
| **Test suite** | ⚠️ Partial | Two of four tests pass (alert_manager, processor). Two fail because the Collector API now requires the `db_dsn` argument; the tests still use the old signature. |
| **Pipeline services** | ✅ Operational | Backend (FastAPI) and Collector have a defined entry point and run correctly. Processor and AlertEngine in Compose are pipeline components; as standalone containers they do not run a long-lived loop. The viable MVP flow is **db + backend + collector**. |

**Conclusion:** The project can be considered a **runnable MVP**. The API, database, collector, and local pipeline (`setup.py`) are usable. For stable use, ensure port 5432 is available (or remap it) for Docker and update the collector tests to use the current signature (required `db_dsn` or equivalent mock).

---

### Prerequisites

- **Python**: 3.11 or higher (3.12 recommended)
- **PostgreSQL**: 14+ (or use the project’s container)
- **Docker and Docker Compose** (optional but recommended for the MVP)

---

### 1. Running with Docker (recommended)

The simplest way to run the full system is with Docker Compose.

#### 1.1 Free port 5432

If PostgreSQL or another service is using port **5432**, free it or stop that service before starting the stack:

```bash
# Example on Linux: check what is using port 5432
sudo ss -tlnp | grep 5432
```

#### 1.2 Start services

From the repository root:

```bash
cd deploy
docker compose up -d
```

Services and ports:

| Service       | Port | Description |
|---------------|------|-------------|
| `db`          | 5432 | PostgreSQL (user `devuser`, DB `coredb`) |
| `backend`     | 8000 | FastAPI API (events, auth, pipeline) |
| `collector`   | 8001 | Event collector (NOTIFY + API) |
| `processor`   | 8002 | Event processor (depends on backend) |
| `alert_engine`| 8003 | Alert engine (depends on backend) |

#### 1.3 View logs

```bash
cd deploy
docker compose logs -f
# Or per service:
docker compose logs -f backend
docker compose logs -f collector
```

#### 1.4 Verify the backend

```bash
curl -s http://localhost:8000/docs
# or
curl -s http://localhost:8000/
```

#### 1.5 Stop and clean up

```bash
cd deploy
docker compose down
# With volumes (removes PostgreSQL data):
docker compose down -v
```

**Note:** The `processor` and `alert_engine` containers are intended to run as part of a queued pipeline; as standalone services with the current CMD they may not keep a long-running process. The full MVP flow (collector → backend) works with **db**, **backend**, and **collector**.

---

### 2. Local execution (without Docker)

Useful for development and testing against a local database.

#### 2.1 Virtual environment and install

```bash
cd /path/to/core_db
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r deploy/requirements.txt
```

#### 2.2 Database

Ensure PostgreSQL is available with a database `coredb` and user `devuser` / password `devpass`, or create one:

```bash
# Example with Docker for DB only
docker run -d --name coredb_pg \
  -e POSTGRES_USER=devuser \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=coredb \
  -p 5432:5432 \
  postgres:16
```

Initialize the schema (if using the repo script):

```bash
psql "postgresql://devuser:devpass@localhost:5432/coredb" -f db/init-scripts/V1_schema_dev.sql
```

#### 2.3 Environment variables

Locally, the backend uses environment variables or a `.env` file. You can export:

```bash
export DATABASE_URL="postgresql://devuser:devpass@localhost:5432/coredb"
export SECRET_KEY="dev-secret-key"
export DB_HOST="localhost"
```

If you use the `.env` in `db/`, the backend’s `database.py` may load it (depending on the working directory).

#### 2.4 Run the backend (API)

From the repo root, with `PYTHONPATH` set to `src`:

```bash
cd /path/to/core_db
export PYTHONPATH=src
uvicorn core.backend.main:app --host 0.0.0.0 --port 8000
```

Check: <http://localhost:8000/docs>.

#### 2.5 Run the full pipeline (collector + processor)

Single process that starts the collector, processor, and worker queue:

```bash
cd /path/to/core_db
export PYTHONPATH=src
export DATABASE_URL="postgresql://devuser:devpass@localhost:5432/coredb"
python src/setup.py
```

This starts the collector (PostgreSQL listener), event processor, and workers; use Ctrl+C to stop.

---

### 3. Verifying build and startup

- **Imports and dependencies** (with venv active and `PYTHONPATH=src`):

  ```bash
  python -c "
  from core.async_lib.async_manager import AsyncManager
  from core.backend.database import engine
  print('Imports OK')
  "
  ```

- **Docker build** (from repo root):

  ```bash
  cd deploy
  docker compose build
  ```

- **Tests** (optional; requires pytest in the venv):

  ```bash
  pip install pytest
  PYTHONPATH=src pytest src/tests/ -v --tb=short
  ```

---

### 4. Quick reference

| Goal              | Command |
|-------------------|--------|
| Run everything with Docker | `cd deploy && docker compose up -d` |
| API only (local)  | `PYTHONPATH=src uvicorn core.backend.main:app --port 8000` |
| Local pipeline    | `PYTHONPATH=src python src/setup.py` |
| Verify imports    | `PYTHONPATH=src python -c "from core.backend.database import engine; print('OK')"` |

For more design and roadmap context, see `docs/plan/09-execution.md` and the repository `README.md`.

---

## [ES] Español

### Conclusiones del estado MVP

Tras revisar compilación, despliegue y pruebas automatizadas, el estado del proyecto se resume así:

| Aspecto | Estado | Notas |
|--------|--------|--------|
| **Compilación e imports** | ✅ Correcto | Con entorno virtual y `PYTHONPATH=src`, los módulos del core (backend, async_lib, base de datos) se importan sin errores. |
| **Build Docker** | ✅ Correcto | `docker compose build` en `deploy/` finaliza correctamente para backend, collector, processor y alert_engine. |
| **Ejecución con Docker** | ⚠️ Depende del entorno | El stack requiere el puerto **5432** libre. Si hay PostgreSQL u otro servicio usándolo, `docker compose up -d` fallará hasta liberar el puerto o reasignar el mapeo. |
| **Suite de tests** | ⚠️ Parcial | Dos de cuatro tests pasan (alert_manager, processor). Dos fallan porque la API del Collector exige el argumento obligatorio `db_dsn`; los tests siguen usando la firma antigua. |
| **Servicios del pipeline** | ✅ Operativos | Backend (FastAPI) y Collector tienen punto de entrada definido y son ejecutables. Processor y AlertEngine en Compose actúan como componentes del pipeline; como contenedores independientes no exponen un bucle de ejecución continua. El flujo MVP viable es **db + backend + collector**. |

**Conclusión:** El proyecto puede considerarse un **MVP ejecutable**. La API, la base de datos, el colector y el pipeline local (`setup.py`) son utilizables. Para un uso estable se recomienda: asegurar el puerto 5432 (o mapear otro) en despliegues Docker y actualizar los tests del collector para usar la firma actual (`db_dsn` obligatorio o mock equivalente).

---

### Requisitos previos

- **Python**: 3.11 o superior (recomendado 3.12)
- **PostgreSQL**: 14+ (o usar el contenedor que incluye el proyecto)
- **Docker y Docker Compose** (opcional pero recomendado para el MVP)

---

### 1. Ejecución con Docker (recomendada)

La forma más sencilla de ejecutar todo el sistema es con Docker Compose.

#### 1.1 Puerto 5432 libre

Si tienes PostgreSQL u otro servicio usando el puerto **5432**, libéralo o detén el servicio antes de levantar el stack:

```bash
# Ejemplo en Linux: comprobar qué usa el puerto 5432
sudo ss -tlnp | grep 5432
```

#### 1.2 Levantar servicios

Desde la raíz del repositorio:

```bash
cd deploy
docker compose up -d
```

Servicios y puertos:

| Servicio     | Puerto | Descripción |
|-------------|--------|-------------|
| `db`        | 5432   | PostgreSQL (usuario `devuser`, DB `coredb`) |
| `backend`   | 8000   | API FastAPI (eventos, auth, pipeline) |
| `collector` | 8001   | Colector de eventos (NOTIFY + API) |
| `processor` | 8002   | Procesador de eventos (depende del backend) |
| `alert_engine` | 8003 | Motor de alertas (depende del backend) |

#### 1.3 Ver logs

```bash
cd deploy
docker compose logs -f
# o por servicio:
docker compose logs -f backend
docker compose logs -f collector
```

#### 1.4 Verificar que el backend responde

```bash
curl -s http://localhost:8000/docs
# o
curl -s http://localhost:8000/
```

#### 1.5 Parar y limpiar

```bash
cd deploy
docker compose down
# Con volúmenes (borra datos de PostgreSQL):
docker compose down -v
```

**Nota:** Los contenedores `processor` y `alert_engine` están pensados para integrarse en un pipeline con cola; si se ejecutan como servicios independientes con el CMD actual, pueden no mantener un proceso en ejecución continua. El flujo MVP completo (colector → backend) funciona con **db**, **backend** y **collector**.

---

### 2. Ejecución local (sin Docker)

Útil para desarrollo y pruebas con una base de datos local.

#### 2.1 Entorno virtual e instalación

```bash
cd /ruta/a/core_db
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r deploy/requirements.txt
```

#### 2.2 Base de datos

Asegúrate de tener PostgreSQL con una base `coredb` y usuario `devuser`/contraseña `devpass`, o crea uno:

```bash
# Ejemplo con Docker solo para la DB
docker run -d --name coredb_pg \
  -e POSTGRES_USER=devuser \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=coredb \
  -p 5432:5432 \
  postgres:16
```

Inicializa el esquema (si usas el script del repo):

```bash
psql "postgresql://devuser:devpass@localhost:5432/coredb" -f db/init-scripts/V1_schema_dev.sql
```

#### 2.3 Variables de entorno

En local, el backend busca por defecto variables de entorno o un `.env`. Puedes exportar:

```bash
export DATABASE_URL="postgresql://devuser:devpass@localhost:5432/coredb"
export SECRET_KEY="dev-secret-key"
export DB_HOST="localhost"
```

Si usas el `.env` en `db/`, el `database.py` del backend puede cargarlo (según la ruta relativa al directorio de ejecución).

#### 2.4 Ejecutar el backend (API)

Desde la raíz del repo, con `PYTHONPATH` apuntando a `src`:

```bash
cd /ruta/a/core_db
export PYTHONPATH=src
uvicorn core.backend.main:app --host 0.0.0.0 --port 8000
```

Comprueba: <http://localhost:8000/docs>.

#### 2.5 Ejecutar el pipeline completo (colector + procesador)

Un solo proceso que arranca colector, procesador y cola de trabajadores:

```bash
cd /ruta/a/core_db
export PYTHONPATH=src
export DATABASE_URL="postgresql://devuser:devpass@localhost:5432/coredb"
python src/setup.py
```

Esto inicia el colector (listener PostgreSQL), el procesador de eventos y los workers; para detenerlo usa Ctrl+C.

---

### 3. Comprobar que el proyecto “compila” y arranca

- **Imports y dependencias** (con venv activado y `PYTHONPATH=src`):

  ```bash
  python -c "
  from core.async_lib.async_manager import AsyncManager
  from core.backend.database import engine
  print('Imports OK')
  "
  ```

- **Build Docker** (desde la raíz):

  ```bash
  cd deploy
  docker compose build
  ```

- **Tests** (opcional; requiere pytest en el venv):

  ```bash
  pip install pytest
  PYTHONPATH=src pytest src/tests/ -v --tb=short
  ```

---

### 4. Resumen rápido

| Objetivo              | Comando principal |
|-----------------------|-------------------|
| Todo con Docker       | `cd deploy && docker compose up -d` |
| Solo API en local     | `PYTHONPATH=src uvicorn core.backend.main:app --port 8000` |
| Pipeline local        | `PYTHONPATH=src python src/setup.py` |
| Verificar imports     | `PYTHONPATH=src python -c "from core.backend.database import engine; print('OK')"` |

Para más contexto de diseño y roadmap, ver `docs/plan/09-execution.md` y el `README.md` del repositorio.
