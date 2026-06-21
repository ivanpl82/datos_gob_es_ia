# Delta: `api-client` — paginación con `result` anidado

## Propósito

Corregir `paginate()` para que extraiga `items` y `next` desde `result` anidado, no desde el nivel raíz del JSON. La API de datos.gob.es devuelve `{"result": {"items": [...], "next": ...}}` — no `{"items": [...], "next": ...}` directamente.

## ADDED Requirements

### Requirement: extraer `result` anidado

`paginate()` SHALL extraer `result` del nivel raíz antes de leer `items` y `next`.

La extracción SHALL ser: `data.get("result", {})` → items desde `result.get("items", [])`, `next` desde `result.get("next")`.

#### Scenario: extracción correcta de items

- GIVEN respuesta de API: `{"format": "json", "version": "1.0", "result": {"items": [{"title": "a"}], "next": "/page2"}}`
- WHEN `paginate()` procesa la respuesta
- THEN llama a `data.get("result", {})` y devuelve `result.get("items", [])` — 1 item
- AND `next` se detecta en `result.get("next")`, no en raíz

#### Scenario: respuesta sin `result`

- GIVEN respuesta: `{"error": "not_found", "message": "..."}`
- WHEN `paginate()` procesa
- THEN `data.get("result", {})` devuelve `{}`
- AND `result.get("items", [])` devuelve `[]`
- AND `result.get("next")` devuelve `None`
- AND `"next" not in result` → True → corta loop

### Requirement: `publisher get` usa `_fetch_page()` directa

El comando `publisher get` SHALL usar `_fetch_page()` para una sola petición en vez de `paginate()`. Esto evita el loop de paginación para una consulta de item único.

(Anteriormente: `publisher get` iteraba sobre `paginate()` y devolvía toda la primera página)

#### Scenario: publisher get con una sola petición

- GIVEN endpoint `catalog/publisher/{id}`
- WHEN se ejecuta `publisher_get`
- THEN `_fetch_page()` se llama una vez
- AND result se extrae como `result["items"][0]`
- AND se devuelve ese único item, no una lista

#### Scenario: publisher get con ID que no existe

- GIVEN endpoint `catalog/publisher/{id_nonexistente}`
- WHEN la API devuelve `{"result": {"items": [], "next": ""}}`
- THEN `_fetch_page()` recibe `{}` como fallback
- AND `result.get("items", [])` → `[]`
- AND `result.get("next")` → `None`
- AND se corta sin error (pero no hay item que emitir)

## MODIFIED Requirements

### Requirement: R8 — Paginación completa

`paginate()` SHALL recorrer `next` hasta que falte, usando el mismo mecanismo de `result` anidado. `next` ahora se lee de `result`, no del raíz del JSON.

(Previously: `paginate()` chequeaba `"next" not in data` en el nivel raíz. Con la estructura actual, `next` está dentro de `result`, así que `"next" in result` — si `result` no tiene `next`, se corta.)

#### Scenario: Paginación detecta `next` anidado

- GIVEN respuesta con estructura `{"result": {"items": [...], "next": "/page2"}}`
- WHEN `paginate()` chequea si hay más páginas
- THEN `"next" in result` → True → continúa iterando
- AND `time.sleep(0.5)` y request a página 2

#### Scenario: Sin `next` en última página

- GIVEN respuesta: `{"result": {"items": [{"title": "z"}], "next": ""}}`
- WHEN `paginate()` chequea `next`
- THEN `result.get("next")` → `""` → falsy → `"next" not in result` → True
- AND corta el loop de paginación

#### Scenario: Sin `result` en respuesta

- GIVEN respuesta: `{"error": "not_found", "message": "not found"}`
- WHEN `paginate()` chequea `next`
- THEN `data.get("result", {})` → `{}`
- AND `"next" not in result` → True (no está en `{}`)
- AND corta el loop — devuelve lista vacía, no error

## REMOVED Requirements

_(None — no se eliminan requisitos. Solo se refinan.)_

## RENAMED Requirements

_(None — no se renombran requisitos.)_

## Notas de implementación

- **Extracción segura**: `data.get("result", {})` — si `result` no existe (edge case), devuelve `{}`, no error
- **Compatibilidad**: todos los comandos que usan `paginate()` (`dataset`, `distribution`, `publisher list`, `theme`, `spatial`, `nti`) se benefician automáticamente — no requieren cambios individuales
- **Tests**: `unittest.mock.patch` para `APIClient._fetch_page` — mockear respuesta real con estructura anidada
- **Rate limiting**: `time.sleep(0.5)` entre páginas — sin cambios