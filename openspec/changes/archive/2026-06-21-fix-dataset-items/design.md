# Design: Fix nested result structure in APIClient paginate()

## Technical Approach

Three focused changes targeting the linked-data-api v0.2 `result` nesting:

1. **`client.py` paginate()**: extract `result` before reading `items`/`next` — cheap, safe, fixes all consumers
2. **`publisher.py` publisher_get**: swap `paginate()` → `_fetch_page()` + extract `result["items"][0]` — single-request for single-item lookup
3. **Tests**: `unittest.mock.patch` on `APIClient._fetch_page` with real API structure — no external deps

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|---|---|---|---|
| Paginate nesting fix | `data.get("result", {})` → `result.get("items", [])` + `"next" not in result` | Keep raíz, add `result` fallback | Two-char fix, safe for missing `result`, compatible with all consumers |
| Publisher get refactor | `_fetch_page()` + `result.get("items", [{}])[0]` | Keep `paginate()` + `next(iter(...))` | `paginate()` iterates; single-item needs no loop. `[{}]` fallback handles empty result |
| Test deps | `unittest.mock` only | `responses`, `requests-mock`, `vcrpy` | Zero external deps, simple `patch` on `_fetch_page`, matches existing test style |
| Test runner | pytest (coexists with ad-hoc) | Force-migrate old tests | `test_*.py` is native to both; no migration cost |

## Data Flow

```
Before (broken):
  API response → data["items"] ❌ (raíz no tiene items)
              → data["next"] ❌ (next nunca está en raíz)
              → loop infinito, devuelve result como item

After (fixed):
  API response → data["result"] → result["items"] ✓
                                → result["next"] ✓
                                → corta cuando no hay next
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/datosgob_cli/client.py` | Modify | Lines 74, 78 — add `result = data.get("result", {})`, use `result.get("items", [])` and `"next" not in result` |
| `src/datosgob_cli/commands/publisher.py` | Modify | `publisher_get` → `_fetch_page()` + `result["items"][0]` extraction; add `result.get("items", [{}])` fallback |
| `tests/test_client.py` | Modify | Add pytest-style tests with `unittest.mock.patch` |

## Interfaces / Contracts

No public API changes. `paginate()` keeps same signature — internal behavior only.

**New guard**: `publisher_get` now returns `{}` on empty result (no break to caller).

```python
# publisher_get — new
result = client._fetch_page(
    f"catalog/publisher/{publisher_id.lstrip('/')}",
    {}
)
item = result.get("items", [{}])[0]
click.echo(format_json(item))
```

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | `paginate()` extrae `result` | `mock.patch("APIClient._fetch_page")` — return `{"result": {"items": [{"title": "x"}], "next": "/p2"}}` |
| Unit | `paginate()` sin `result` | Return `{"error": "not_found"}` → `items = []`, `next` no en `result` → corta |
| Unit | `paginate()` ultima pagina | Return `{"result": {"items": [{"title": "z"}], "next": ""}}` → `"next" not in result` → break |
| Unit | `publisher_get` id existe | Return `{"result": {"items": [{"id": 1, "title": "Pub"}]}}` → `[{"id": 1, "title": "Pub"}]` |
| Unit | `publisher_get` id no existe | Return `{"result": {"items": []}}` → `{}` |

## Migration / Rollout

No migration required. Old tests (`test_client_exists` etc.) coexist — no rename. New tests go in same file with `test_` prefix; pytest picks them up.

## Open Questions

- [ ] Confirm: `publisher_get` return value — `{}` vs `None` vs `click.echo("Not found")`? Spec says `{}` on empty result.

## Design Notes

- `result.get("items", [{}])[0]` with `[{}]` fallback: if `items` is `[]`, `items[0]` → `{}` → `click.echo(format_json({}))` → user sees `{}` instead of crash. Intentional.
- `"next" not in result` idiom: when `result` has no `next` key (empty string or absent), `"next" not in result` is `True` → break loop.
- Comment added: `# linked-data-api v0.2: data["result"] wraps items/next` — prevents regression.