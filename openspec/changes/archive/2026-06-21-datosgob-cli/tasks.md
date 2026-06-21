# Tasks: `datosgob-cli`

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas estimadas cambiadas | 450–650 (Python) + 100 (SKILL.md) = ~550–750 |
| Riesgo presupuesto 400 líneas | **Alto** |
| PRs encadenados recomendados | **Sí** |
| División sugerida | PR 1: infraestructura + comandos (≈300–400 líneas) → PR 2: tests + SKILL.md (≈200–250 líneas) |
| Estrategia de entrega | `auto-chain` |
| Estrategia de cadena | `feature-branch-chain` |

```
Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High
```

### Suggested Work Units

| Unidad | Objetivo | PR probable | Notas |
|--------|----------|-------------|-------|
| 1 | Infraestructura + comandos | PR 1 (→ `datosgob-cli` branch) | `pyproject.toml`, `client.py`, `commands/`, `cli.py`, `formatters.py` |
| 2 | Tests + documentación | PR 2 (→ base PR 1 branch) | `tests/`, `SKILL.md`. Depende de PR 1 |

---

## Fase 1: Infraestructura / Fundación

- [x] 1.1 Crear `src/datosgob_cli/` package directory + `__init__.py` con `__version__ = "0.1.0"`
- [x] 1.2 Crear `pyproject.toml` — `[project]` metadata, `dependencies` (`click>=8.1`, `requests>=2.31`, `pandas>=2.0`), `[project.scripts]` (`datosgob = "...cli:main"`), `[tool.ruff]` config
- [x] 1.3 Implementar `src/datosgob_cli/client.py` — `APIClient` con `requests.Session`, `_fetch_page()` (GET + timeout), `paginate()` (generador, recorre `next` hasta que falte), manejo de `HTTPError` y `ConnectionError`
- [x] 1.4 Implementar `src/datosgob_cli/formatters.py` — `format_json()`, `format_csv()` (con cabeceras), `format_pandas()` (DataFrame → JSON serializado)

## Fase 2: Comandos CLI / Núcleo

- [x] 2.1 Implementar `src/datosgob_cli/cli.py` — `@click.group()` → `cli()` con `--format`, `--pandas`, `--page-size` como opciones globales; `main()` como entry point
- [x] 2.2 Implementar `src/datosgob_cli/commands/dataset.py` — `@click.command('dataset')`, filtros `--theme`, `--publisher`, `--keyword`, `--format`, `--spatial`, `--modified-begin/end`, `--issued-begin/end`; llama a `client.paginate()` y formatea salida
- [x] 2.3 Implementar `src/datosgob_cli/commands/distribution.py` — `@click.command('distribution')`, filtros `--by-dataset`, `--by-format`
- [x] 2.4 Implementar `src/datosgob_cli/commands/publisher.py` — `@click.command('publisher')`, subcomandos `list` y `get {id}` (parámetro posicional)
- [x] 2.5 Implementar `src/datosgob_cli/commands/theme.py` — `@click.command('theme')`, listado simple
- [x] 2.6 Implementar `src/datosgob_cli/commands/spatial.py` — `@click.command('spatial')`, listado simple
- [x] 2.7 Implementar `src/datosgob_cli/commands/nti.py` — `@click.command('nti')`, filtros `--sector`, `--territory`
- [x] 2.8 Registrar todos los subcomandos en el `@click.group()` de `cli.py` — `cli.add_command(dataset_cmd)`, etc.

## Fase 3: Pruebas

- [x] 3.1 Crear `tests/__init__.py` — paquete de tests con docstring
- [x] 3.2 Crear `tests/test_client.py` — tests de inspección: APIClient se instancia, base_url default, `_session` es Session, page_size capped a 50, custom base_url
- [x] 3.3 Crear `tests/test_commands.py` — tests de inspección: todos los módulos de comandos se importan, CLI group registra exactamente 6 comandos
- [x] 3.4 Verificar funcionamiento: `python3 tests/test_client.py` + `python3 tests/test_commands.py` + `python3 src/datosgob_cli/cli.py --help` — todo OK sin errores

## Fase 4: Documentación / Cierre

- [x] 4.1 Crear `SKILL.md` — documentación para OpenCode: trigger, uso, comandos disponibles, ejemplos, notas técnicas