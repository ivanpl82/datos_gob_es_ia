# `datosgob-api-cli` — Especificación

## Propósito

Script CLI que consume la API de datos.gob.es (linked-data-api v0.2) y expone los verbos de catálogo como subcomandos `click`. El usuario obtiene datos abiertos desde terminal sin consultas HTTP manuales.

## Resumen de requisitos

| ID | Subcomando | Obligación | Escenarios |
|----|-------------|------------|------------|
| R1 | `datosgob` (entry) | **DEBE** exponer Group con todos los subcomandos | `--help` lista todos |
| R2 | `dataset` | **DEBE** consultar `/dataset` con filtros | Listado con `--theme`, API caída timeout |
| R3 | `distribution` | **DEBE** filtrar por `--by-dataset` y `--by-format` | Distribuciones asociadas |
| R4 | `publisher` | **DEBE** devolver listado y `--get {id}` | Listar publishers |
| R5 | `theme` | **DEBE** listar temas | Listar temas |
| R6 | `spatial` | **DEBE** listar coberturas | Listar coberturas |
| R7 | `nti` | **DEBE** consultar por `--sector` y `--territory` | NTI por sector |
| R8 | Paginación | **DEBE** recorrer `next` hasta que falte | Recorrido completo, sin siguiente |
| R9 | Salida | **DEBE** soportar `--format json\|csv` y `--pandas` | JSON, CSV, DataFrame |
| R10 | Filtros | **DEBE** aplicar al endpoint correcto | Filtro válido, filtro inválido |
| R11 | Errores | **DEBE** manejar timeout, HTTP, caída | Timeout, HTTP 4xx/5xx |

## Escenarios detallados

### R2 — Listado de datasets

- DADO: `datosgob dataset list --theme salud`
- CUANDO: la API responde HTTP 200
- ENTONCES: se devuelven `items` en el formato solicitado
- Y: si expira el timeout, mensaje de error + exit code 1

### R3 — Distribuciones por dataset

- DADO: `datosgob distribution list --by-dataset urn:uuid:...`
- CUANDO: la API devuelve los `items`
- ENTONCES: se muestran las distribuciones del dataset

### R4 — Listado de publishers

- DADO: `datosgob publisher list`
- CUANDO: la API responde
- ENTONCES: se devuelven todos los publishers
- Y: `datosgob publisher get {id}` devuelve el publisher individual

### R8 — Paginación completa

- DADO: solicitud sin `--page` límite
- CUANDO: el cliente recibe `next` en la respuesta
- ENTONCES: solicita la página siguiente
- Y: continúa hasta que `next` esté ausente — entonces devuelve todos los `items` acumulados

### R9 — Formato de salida

| Flag | DADO | ENTONCES |
|------|------|----------|
| `--format json` | sin opción | Salida JSON estándar |
| `--format csv` | sin opción | Salida CSV con cabeceras |
| `--pandas` | sin opción | DataFrame serializado (JSON) |

### R10 — Filtro no válido

- DADO: filtro que no existe en el endpoint
- CUANDO: el comando procesa el argumento
- ENTONCES: error informado + exit code 2

### R11 — Error HTTP

- DADO: la API responde HTTP 4xx o 5xx
- CUANDO: `requests` detecta el código
- ENTONCES: se muestra el código y cuerpo del error en stderr
- Y: exit code 1

## Notas de implementación

- **Rate limiting**: `time.sleep(0.5)` entre páginas
- **`_pageSize`**: máximo 50, default 10
- **Filtros**: `--theme`, `--publisher`, `--keyword`, `--format`, `--spatial`, `--modified-begin/end`, `--issued-begin/end`
- **`--pandas`**: salida como `DataFrame` con `pandas>=2.0`