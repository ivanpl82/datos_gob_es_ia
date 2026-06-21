# Diseño: `datosgob-cli`

## Enfoque técnico

Paquete Python (`datosgob-cli`) de tres capas que expone la API de datos.gob.es como subcomandos `click`. El usuario invoca desde terminal o desde el LLM via `SKILL.md`; el cliente recorre la paginación linked-data-api v0.2, aplica filtros, y devuelve resultados formateados.

## Decisiones de arquitectura

### Decisión: `requests.Session` con timeout + retry vs `httpx`

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| `requests.Session` | Síncrono, más simple, sin dependencias extra | ✅ Elegido |
| `httpx` | Async nativo, cliente HTTP/2 | ❌ Rechazado — proyecto verde, sin necesidad de async |

**Racional**: `requests` es el estándar de facto de Python para APIs síncronas. `httpx` agregaría complejidad sin beneficio real para un CLI que hace una request por página secuencialmente.

### Decisión: `click` como framework CLI vs `argparse` / `typer`

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| `click` | Decoradores, auto-help, subcomandos anidados | ✅ Elegido |
| `argparse` | Más verboso, sin auto-help formateado | ❌ Rechazado |
| `typer` | Sobre `typer` + `click`, menos maduro | ❌ Rechazado |

**Racional**: `click` es el framework más usado en ecosistema Python CLI. El decorador `@click.group` + `@click.command` es el patrón documentado y testado para este caso de uso.

### Decisión: Paginación como generador Python

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| Generador `yield` | Lazy, no carga todo en memoria | ✅ Elegido |
| Carga completa en lista | Sencillo pero puede explotar RAM | ❌ Rechazado |

**Racional**: La API no tiene `totalCount`. Un generador que recorre `next` hasta que falte es la única estrategia correcta — y encima es eficiente en memoria.

### Decisión: Pandas como capa opcional (`--pandas` flag)

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| DataFrame → JSON serializado | El LLM recibe un DataFrame listo para análisis | ✅ Elegido |
| Devuelve raw JSON siempre | Sin contexto de análisis | ❌ Rechazado |

**Racional**: `--pandas` convierte los `items` a `pandas.DataFrame` y lo serializa a JSON. El LLM recibe datos estructurados que puede analizar inmediatamente sin parsear manualmente.

### Decisión: `ruff` como linter + formatter unificado

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| `ruff` | Linter + formatter en uno, más rápido | ✅ Elegido |
| `flake8` + `black` | Dos herramientas, más configuración | ❌ Rechazado |

**Racional**: Ruff es el estándar moderno de Python. Un solo `pyproject.toml` para todo.

## Flujo de datos

```
Usuario/LLM ──→ datosgob dataset list --theme salud
                    │
                    ▼
              cli.py (entry point)
                    │
                    ▼
         commands/dataset.py
              ┌─┴─┐
              │   │
              ▼   ▼
         client.py ───→ GET /api/datos/dataset?theme=salud&_pageSize=10
                              │
                              ▼
                         datos.gob.es (HTTP 200)
                              │
                              ▼
                   ← JSON con {items, next}
                              │
                    ┌─ next? ─┤
                    │          │
                    ▼          └──→ más páginas
                 acumula        (recursión generador)
                 items
                    │
                    ▼
              formateador (json/csv/pandas)
                    │
                    ▼
                stdout (exit 0)
```

## Cambios de archivos

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/datosgob_cli/__init__.py` | Crear | Paquete vacío, `__version__` |
| `src/datosgob_cli/client.py` | Crear | `APIClient` — `requests.Session`, `_fetch_page()`, `paginate()` (generador), manejo de errores |
| `src/datosgob_cli/commands/__init__.py` | Crear | Re-exporta todas las funciones `click` |
| `src/datosgob_cli/commands/dataset.py` | Crear | `@click.command('dataset')`, filtros `--theme`, `--publisher`, `--keyword`, `--format`, `--spatial`, `--modified-begin/end`, `--issued-begin/end` |
| `src/datosgob_cli/commands/distribution.py` | Crear | `@click.command('distribution')`, filtros `--by-dataset`, `--by-format` |
| `src/datosgob_cli/commands/publisher.py` | Crear | `@click.command('publisher')`, `list` y `get {id}` |
| `src/datosgob_cli/commands/theme.py` | Crear | `@click.command('theme')`, listar |
| `src/datosgob_cli/commands/spatial.py` | Crear | `@click.command('spatial')`, listar |
| `src/datosgob_cli/commands/nti.py` | Crear | `@click.command('nti')`, `--sector`, `--territory` |
| `src/datosgob_cli/cli.py` | Crear | `@click.group()` → `cli()`, `main()`, `--format`, `--pandas`, `--page-size` |
| `src/datosgob_cli/formatters.py` | Crear | `format_json()`, `format_csv()`, `format_pandas()` — salida estandarizada |
| `tests/test_client.py` | Crear | Tests unitarios con `responses` mock |
| `tests/test_commands.py` | Crear | Tests de integración contra API real |
| `tests/test_formatters.py` | Crear | Tests de formato (json, csv, pandas) |
| `pyproject.toml` | Crear | Dependencias, configuración `ruff`, `[project.scripts]` para entry point |
| `SKILL.md` | Crear | Documentación para el LLM de OpenCode |

## Interfaces / Contratos

```python
# client.py
class APIClient:
    def __init__(self, base_url: str, timeout: int = 10, page_size: int = 10): ...
    
    def fetch(self, endpoint: str, params: dict) -> dict:
        """GET con timeout configurable. Lanza HTTPError si 4xx/5xx."""
    
    def paginate(self, endpoint: str, params: dict) -> Generator[list[dict], None, None]:
        """Generador: recorre next hasta que falte. Cada yield es una página."""

# formatters.py
def format_json(items: list[dict]) -> str: ...
def format_csv(items: list[dict]) -> str: ...
def format_pandas(items: list[dict]) -> str:
    """DataFrame → JSON. Solo si --pandas está activo."""

# commands/dataset.py
@click.command('dataset')
@click.option('--theme', default=None)
@click.option('--format', type=click.Choice(['json', 'csv']))
@click.option('--pandas', is_flag=True)
def dataset_cmd(theme, format, pandas, ...): ...
```

## Estrategia de testing

| Capa | Qué testear | Cómo |
|------|-------------|------|
| Unidad | `APIClient.fetch`, `APIClient.paginate`, formateo | `responses` mock — simular respuestas HTTP |
| Integración | Cada endpoint contra API real | `pytest` + `requests` real — `timeout=15`, `_pageSize=10` |
| E2E | Pipeline completo: `dataset --theme` → stdout | `subprocess.run(["datosgob", ...])` |

## Manejo de errores

| Error | Comportamiento | Exit code |
|-------|---------------|-----------|
| Timeout (30s) | `stderr`: "La API no respondió en 30s" | 1 |
| HTTP 4xx | `stderr`: código + cuerpo del error | 1 |
| HTTP 5xx | `stderr`: "Error del servidor" + body | 1 |
| JSON malformado | `stderr`: "Respuesta no válida" | 1 |
| API caída | `stderr`: timeout, exit code 1 | 1 |

## Migración / Rollout

Sin migración requerida — proyecto verde. `git init` + primer commit.

## Preguntas abiertas

- [ ] Ninguna — el diseño es completo para lo que cubre la propuesta y la especificación.