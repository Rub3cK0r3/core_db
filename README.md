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

## 📖 Documentación

* `docs/async_manager.md` – Funciones y flujo de eventos
* `docs/event_pipeline.md` – Diagramas y ejemplos
* `docs/examples.md` – Pipelines completos y testcases

---

## 🔒 Seguridad

* RBAC en todos los endpoints
* Logs **tamper-evident**
* Validación de inputs y protección contra inyecciones
* Anomaly detection para eventos sospechosos
* Pentesting de contenedores y autenticación

---

## 📌 Issues iniciales sugeridos

1. **Integrar logging tamper-evident** – Hash logs y encadenado.
2. **Agregar tests de integración** – Ingesta → procesador → alertas.
3. **Crear ejemplo de alerta CLI** – Basado en `pipeline.py`.
4. **Documentar AsyncManager** – Explicar flujo de eventos y hooks.
5. **Docker Compose básico** – Levantar collector + processor + DB.

---

## 📝 Licencia

MIT License © 2026
