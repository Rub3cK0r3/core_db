# core-db-mini-problemas.md

* [ ] **Conexión a la base de datos**

  * [ ] Leer variables de entorno (host, puerto, user, password, dbname)
  * [ ] Conectar a la base de datos con pooling
  * [ ] Manejar errores de conexión inicial y reconexión automática
  * [ ] Diferenciar entornos dev / test / prod

* [ ] **Esquema y migraciones**

  * [ ] Definir tablas, columnas, tipos y relaciones
  * [ ] Crear constraints (PK, FK, unique, not null)
  * [ ] Versionar esquema para migraciones incrementales
  * [ ] Scripts CLI para migraciones automáticas
  * [ ] Rollback seguro de migraciones

* [ ] **CRUD básico**

  * [ ] Insertar registros con validación de datos
  * [ ] Leer registros (select) con filtros simples
  * [ ] Actualizar registros de manera segura
  * [ ] Eliminar registros con chequeo de relaciones
  * [ ] Manejar errores de integridad (FK, unique)
  * [ ] Logging de operaciones críticas

* [ ] **Consultas complejas y filtros**

  * [ ] Joins entre tablas relacionadas
  * [ ] Agregaciones (sum, count, avg)
  * [ ] Paginación y ordenamiento
  * [ ] Filtros dinámicos (por usuario, fecha, estado)
  * [ ] Manejo de resultados grandes (streaming o chunks)
  * [ ] Optimización con índices en columnas críticas

* [ ] **Transacciones y atomicidad**

  * [ ] Agrupar operaciones en transacciones
  * [ ] Rollback automático ante fallo parcial
  * [ ] Soporte para transacciones anidadas si aplica
  * [ ] Manejo de locks y deadlocks

* [ ] **Integridad de datos**

  * [ ] Constraints DB + validación backend
  * [ ] Sanitización de inputs para evitar SQLi
  * [ ] Chequeo de relaciones consistentes entre tablas
  * [ ] Monitoreo de datos “huérfanos” o inconsistentes

* [ ] **Rendimiento e indexación**

  * [ ] Crear índices para columnas de búsqueda frecuente
  * [ ] Identificar queries lentas y optimizarlas
  * [ ] Cache opcional para queries pesadas
  * [ ] Benchmark de inserciones y consultas

* [ ] **Logging y auditoría**

  * [ ] Registrar todas las operaciones críticas
  * [ ] Timestamps y usuario responsable
  * [ ] Guardar logs de cambios importantes
  * [ ] CLI para consultar auditoría

* [ ] **Seguridad y acceso**

  * [ ] Autenticación de usuarios backend
  * [ ] Autorización / RBAC (roles admin, dev, analista)
  * [ ] Encriptación de datos sensibles (reposo y tránsito)
  * [ ] Protección contra SQL injection y abusos de API

* [ ] **Backup y restauración**

  * [ ] Scripts CLI para backup completo
  * [ ] Scripts CLI para backup incremental
  * [ ] Restore de datos a estado consistente
  * [ ] Validación de integridad de backup
  * [ ] Pruebas automáticas de restauración

* [ ] **Replicación y alta disponibilidad (opcional avanzado)**

  * [ ] Configurar replicas de lectura
  * [ ] Failover automático o manual
  * [ ] Sincronización de datos entre nodos
  * [ ] Monitoreo de latencia y divergencia

* [ ] **Batch y pipelines de procesamiento**

  * [ ] Procesamiento de datos masivos (import/export)
  * [ ] Scripts para migraciones o transformaciones masivas
  * [ ] Manejo de errores en lotes grandes
  * [ ] Logging y métricas de ejecución de pipelines

* [ ] **Pruebas**

  * [ ] Unit tests para queries y lógica
  * [ ] Integration tests con DB real
  * [ ] Performance tests (bulk inserts, queries complejas)
  * [ ] Security tests (SQLi, acceso no autorizado, edge cases)

* [ ] **CLI de administración**

  * [ ] Comando `migrate`
  * [ ] Comando `status`
  * [ ] Comando `backup` / `restore`
  * [ ] Comando `query` / `audit`
  * [ ] Salida formateada (JSON, tablas)
  * [ ] Logging de ejecución de cada comando

* [ ] **Observabilidad y métricas**

  * [ ] Contadores de queries por tipo
  * [ ] Latencia media de consultas
  * [ ] Conteo de errores
  * [ ] Export de métricas a Prometheus / otros
  * [ ] Alertas de saturación de DB o errores críticos

* [ ] **Configuración modular**

  * [ ] Separar conexión DB, modelos, lógica de negocio y CLI
  * [ ] Configuración de entornos con `.env` o YAML
  * [ ] Capacidad de cambiar DB backend sin romper lógica
  * [ ] Modularización de scripts de administración y pipelines

---

Perfecto. Ahora vamos a generar una **versión de checklist de mini pruebas de concepto (PoC)** para Core-DB. La idea es que **cada prueba sea pequeña, ejecutable en terminal, y valide un concepto clave del sistema** antes de implementarlo completo. Esto te permite ir “prototipando” sin liarte con todo el proyecto.

---

# core-db-pocs.md

### 1. Conexión y entornos

* [ ] Probar conexión a Postgres/SQLite desde Python con variables de entorno

  * `python3 -c "import psycopg2; conn=psycopg2.connect(...)"`
* [ ] Reconexión automática tras cierre de conexión simulada
* [ ] Diferenciar entornos: dev/test/prod (leer `.env` y conectarse a DB correcta)

### 2. Esquema y migraciones

* [ ] Crear tabla simple con PK y un índice
* [ ] Insertar y borrar registros
* [ ] Ejecutar migración incremental (agregar columna nueva)
* [ ] Rollback de migración manual

### 3. CRUD básico

* [ ] Insertar registro válido y leerlo
* [ ] Intentar insertar registro inválido (violación de constraint) y capturar error
* [ ] Actualizar un registro y verificar el cambio
* [ ] Borrar un registro y confirmar eliminación

### 4. Consultas complejas

* [ ] Join entre dos tablas de prueba
* [ ] Agregación COUNT y SUM
* [ ] Paginación de resultados con LIMIT/OFFSET
* [ ] Filtrado dinámico por columna y rango de fechas

### 5. Transacciones

* [ ] Insertar múltiples registros en una transacción y hacer rollback
* [ ] Simular deadlock simple entre dos conexiones y detectar error
* [ ] Nested transactions: rollback parcial

### 6. Integridad

* [ ] Probar constraints FK entre tablas
* [ ] Intentar insertar un valor que rompa la relación FK y capturar error
* [ ] Sanitización de inputs: prueba con caracteres especiales (SQL injection)

### 7. Rendimiento

* [ ] Insertar 10k registros en bucle y medir tiempo
* [ ] Ejecutar query compleja y medir latencia
* [ ] Probar índice en columna de búsqueda y comparar velocidad

### 8. Logging y auditoría

* [ ] Registrar insert/update/delete en log de auditoría
* [ ] Consultar log y verificar timestamps y usuario
* [ ] CLI rápido para listar últimas operaciones

### 9. Seguridad y acceso

* [ ] Crear usuario con rol “read-only” y probar acceso
* [ ] Crear usuario “admin” y probar CRUD completo
* [ ] Intentar operación no permitida y verificar error

### 10. Backup / Restore

* [ ] Exportar tabla de prueba a SQL o CSV
* [ ] Importar tabla y verificar consistencia
* [ ] Probar restore de backup completo

### 11. Batch / Pipelines

* [ ] Importar dataset pequeño (100 registros) y validar insert correcto
* [ ] Transformar datos antes de insert (normalize, hash)
* [ ] Log de cada batch

### 12. Pruebas unitarias y de integración

* [ ] Unit test de función insert
* [ ] Unit test de query con filtro dinámico
* [ ] Integration test: insertar y luego leer desde otra conexión
* [ ] Performance test simple: 1k inserts consecutivos

### 13. CLI de administración

* [ ] Ejecutar `status` y mostrar conexiones activas
* [ ] Ejecutar `migrate` en modo dry-run
* [ ] Ejecutar `backup` y validar archivo generado
* [ ] Ejecutar `query` y mostrar resultado formateado en tabla

### 14. Observabilidad / métricas

* [ ] Contar número de queries por tipo en logs
* [ ] Medir tiempo medio de inserts
* [ ] Mostrar número de errores por tipo en CLI

### 15. Configuración modular

* [ ] Cargar configuración desde `.env`
* [ ] Cambiar backend de SQLite a Postgres en test y validar CRUD
* [ ] Separar scripts CLI de modelos y lógica de negocio
