# Propuesta: `datosgob-cli`

## Intención

Crear un **script CLI** (`datosgob-cli`) que exponga la API de datos.gob.es como subcomandos consumibles desde terminal y desde OpenCode. Sin este script, acceder a datos abiertos españoles requiere construir consultas HTTP manuales y parsear el formato linked-data-api v0.2 — trabajoso, propenso a errores, y no integrable con el flujo de trabajo del LLM.

El script resuelve la brecha entre tener datos abiertos disponibles y poderlos usar efectivamente en análisis, experimentación o generación de informes.

## Alcance

### Incluye
- Script CLI con `click` que expone todos los verbos de catálogo como subcomandos (`dataset`, `distribution`, `publisher`, `theme`, `spatial`, `nti`)
- Iterador de paginación que recorre páginas hasta que desaparezca `next` (sin `totalCount`)
- Filtros por endpoint: `--theme`, `--publisher`, `--keyword`, `--format`, `--spatial`, `--modified-begin/end`, `--issued-begin/end`
- Salida en JSON y CSV (`--format json|csv`)
- Salida como `DataFrame` de pandas — el usuario puede pasar `--pandas` y obtener un DataFrame listo para análisis
- Tests con pytest contra datos reales de la API
- Configuración con ruff (linter + formatter)
- Documentación (`SKILL.md`) para que el LLM de OpenCode sepa cómo usar el script

### Excluye
- Caché local de datasets — los datos siempre viajan frescos de la API
- MCP server o cualquier otra integración que no sea `openspec` + script CLI

## Capacidades

### Nuevas capacidades
- `datosgob-api-cli`: script CLI que consume la API de datos.gob.es (linked-data-api v0.2) y expone todos los verbos de catálogo como subcomandos `click`. Incluye paginación automática, filtros por endpoint, y salida JSON/CSV.

### Capacidades modificadas
None — no hay capacidades existentes que modificar.

## Enfoque

1. **`src/datosgob_cli/`** — paquete Python con tres capas:
   - `client.py` — `requests` + manejo de paginación (recorre `items` → `next` hasta que falte)
   - `commands/` — un módulo por verbo de API (`dataset.py`, `distribution.py`, `publisher.py`, etc.), cada uno con su función `click`
   - `cli.py` — entry point `click.group` que agrupa todos los subcomandos
2. **`tests/`** — `pytest` contra la API real. Por cada endpoint, un test que verifica:
   - Respuesta 200
   - Clave `items` presente
   - Paginación funciona (al menos 1 página extra)
   - `--format` cambia la salida
3. **`pyproject.toml`** — configuración: `ruff`, `click>=8.1`, `requests>=2.31`
4. **`SKILL.md`** — documenta el script, sus comandos, y cuándo (y cómo) debe invocar el LLM

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|------------|
| `src/datosgob_cli/` | Nuevo | Paquete raíz con client, CLI, y módulos de comandos |
| `tests/` | Nuevo | Tests de integración contra API real |
| `pyproject.toml` | Nuevo | Configuración de dependencias y herramientas |
| `SKILL.md` | Nuevo | Documentación para el LLM de OpenCode |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| La API de datos.gob.es puede aplicar rate-limiting sin aviso | Media | Usar `_pageSize=10` por defecto, `time.sleep(0.5)` entre requests de paginación |
| El formato `linked-data-api` no tiene `totalCount` — imposible saber cuántas páginas quedan | Alta | El iterador recorre hasta que falte `next`; no hay alternativa |
| Sin autenticación pero el endpoint puede cambiar | Baja | `requests.Session` con timeout configurable; tests contra la URL real cada CI |

## Plan de reversión

- `git revert` del commit de creación de `datosgob-cli`
- Eliminar `src/datosgob_cli/`, `tests/`, y `pyproject.toml`
- Actualizar `openspec/changes/datosgob-cli/state.yaml` a `phase: none`

## Dependencias

- `requests>=2.31` — HTTP sync
- `click>=8.1` — CLI framework
- `pandas>=2.0` — salida como DataFrame para análisis
- `pytest>=7.0` — tests
- `ruff>=0.3` — linter + formatter

## Criterios de éxito

- [x] `datosgob dataset list --theme salud` devuelve resultados correctos (respuesta 200, `items` no vacío)
- [x] `datosgob dataset list --format csv` produce CSV válido
- [ ] Los tests de integración pasan contra la API real (CI puede fallar si la API está caída — acceptable)
- [ ] `datosgob --help` muestra todos los subcomandos correctamente