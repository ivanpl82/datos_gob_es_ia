# Proposal: Fix nested result structure in APIClient paginate()

## Intent

`paginate()` en `client.py` asume que `items` y `next` están en el nivel raíz del JSON de la API. La API de datos.gob.es devuelve `{"result": {"items": [...], "next": ...}}`. Esto hace que `paginate()` devuelva el dict `result` completo como si fuera una página de items, y la paginación nunca termina porque `next` no está en el nivel raíz.

## Scope

### In Scope
- Fix `client.py` líneas 74 y 78 — extraer `result` anidado antes de leer `items`/`next`
- Refactor `publisher` command `get` — usa `_fetch_page()` directo, extrae item único de `result.items[0]`
- Tests — migrar a pytest con mocking de estructura JSON real de la API
- Documentación — comentar el nesting en `client.py` para evitar regresión

### Out of Scope
- Refactor del resto de comandos (todos usan `paginate()`, se corrigen solos)
- Migrar a httpx/asyncio — cache para PR posterior
- Agregar validación de schema de la API

## Capabilities

### New Capabilities
- `api-client-pagination`: Manejo correcto de nested `result` en paginación

### Modified Capabilities
- `api-client`: El contrato de `paginate()` cambia de "itera sobre items planos" a "extrae `result` anidado"

## Approach

- `client.py`: `data.get("result", {})` → `items = result.get("items", [])`, `"next" not in result`
- `publisher.py` `publisher_get`: reemplazar `paginate()` por `_fetch_page()` directo + `result["items"][0]`
- Tests: fixture `response_fixture.json` con la estructura real de la API, `responses` mock para simular paginación

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/datosgob_cli/client.py` | Modified | Líneas 74, 78 — corregir path de `items`/`next` |
| `src/datosgob_cli/commands/publisher.py` | Modified | Refactor `publisher_get` — de `paginate()` a `_fetch_page()` |
| `tests/test_client.py` | New | Tests con mocking de estructura real |
| `tests/test_commands.py` | New | Tests de `publisher_get` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Algún endpoint no tenga la estructura `result.items` | Low | Confirmar con `dataset list` y `publisher list`; ambos usan el mismo patrón |
| Rate limiting en tests con mocking | Low | Usar `responses` o `unittest.mock` — no conexión real |
| `publisher_get` cambia de signatura | Med | Refactor interno; sin breaking change público |

## Rollback Plan

Revertir las 2 líneas en `client.py` y restaurar `publisher_get` a su forma original. Los tests actuales son placeholder y no fallarán.

## Dependencies

- `responses` (o `unittest.mock` nativo) para mocking HTTP en tests

## Success Criteria

- [ ] `test_mocked_paginate()` pasa con fixture de respuesta real (`{"result": {"items": [...], "next": "..."}}`)
- [ ] `datosgob --page-size 2 dataset list` devuelve datasets reales (no keys del JSON)
- [ ] `publisher get <id>` devuelve el item único, no una lista de una página