# Tasks: Fix nested result structure in APIClient paginate()

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~90-110 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |
| Decision needed before apply | No |

## Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Fix paginate + publisher_get + tests | PR 1 | Single PR; all changes fit under 400 lines |

## Phase 1: Foundation / Infrastructure

- [x] 1.1 **Fix `paginate()` in `client.py`** — lines 74-78: extract `result = data.get("result", {})`, read `items` from `result.get("items", [])`, check `"next" not in result` (not `data`). Add comment: `# linked-data-api v0.2: data["result"] wraps items/next`
- [x] 1.2 **Refactor `publisher_get` in `publisher.py`** — replace `for page in client.paginate(...)` with `result = client._fetch_page(...)` + `item = result.get("items", [{}])[0]`, emit single item. Add `result.get("items", [])` fallback for empty result.
- **Files**: `src/datosgob_cli/client.py`, `src/datosgob_cli/commands/publisher.py`
- **Note**: Both changes are in Phase 1 — they fix the data path. T1 and T2 are independent in code but conceptually ordered (T1 first).

## Phase 2: Core Implementation

No Phase 2 — the entire change is the 2 files above.

## Phase 3: Testing / Verification

- [x] 3.1 **Test: `paginate()` happy path** — mock `_fetch_page` returns `{"result": {"items": [{"title": "a"}], "next": "/p2"}}`. Assert `next()` yields 1 item, `"next" in result` keeps loop.
- [x] 3.2 **Test: `paginate()` sin `result`** — mock returns `{"error": "not_found"}`. Assert `data.get("result", {})` → `{}`, `result.get("items", [])` → `[]`, `"next" not in result` → stops immediately without error.
- [x] 3.3 **Test: `paginate()` última página** — mock returns `{"result": {"items": [{"title": "z"}], "next": ""}}`. Assert `"next" not in result` → True (empty string is falsy but absent key → key not in dict) → break.
- [ ] 3.4 **Test: `publisher_get` con ID existente** — mock `_fetch_page` returns `{"result": {"items": [{"id": 1, "title": "Pub"}]}}`. Use `unittest.mock.patch` on `APIClient._fetch_page`. Assert single call, single item output.
- [ ] 3.5 **Test: `publisher_get` con ID no existente** — mock returns `{"result": {"items": []}}`. Assert `result.get("items", [{}])[0]` → `{}` → no crash, empty dict emitted.
- **Files**: `tests/test_client.py`
- **Note**: All tests use `unittest.mock.patch` — no external deps. Coexist with existing ad-hoc tests.

## Phase 4: Verification / Integration

- [ ] 4.1 **Verify `datosgob --page-size 2 dataset list`** — run with real API (no mock). Assert returns real dataset objects (title, description, publisher), not JSON keys.
- [ ] 4.2 **Verify `datosgob dataset list --keyword salud`** — runs without error, returns filtered results.
- [ ] 4.3 **Verify `publisher list`, `theme list`, `spatial list`, `nti list`** — all use `paginate()`; assert no regressions. Each command should return data, not `result` keys.
- [ ] 4.4 **Verify `publisher get <id>`** — returns single publisher dict, not a list wrapped in a page.
- **Note**: Manual integration check. Run after T1+T2+T3 pass.

---

## Implementation Order

1. **T1** (`client.py`) — fix the data extraction path. All other commands depend on this.
2. **T2** (`publisher.py`) — swap to `_fetch_page()`. Builds on the correct `paginate()` behavior.
3. **T3** (tests) — mock-based, no real API. Run after T1+T2 to verify.
4. **T4** (integration) — manual. Run after all unit tests pass.

---

## Acceptance Criteria per Task

### T1 — Fix paginate()
**ID**: T1
**Title**: Correct `result` nesting in `paginate()`
**Description**: Extract `result` from `data` before reading `items`/`next`. Two-line change on lines 74/78.
**Files**: `src/datosgob_cli/client.py`
**Acceptance**: `paginate()` reads `data["result"]["items"]` instead of `data["items"]`. `"next" not in result` terminates pagination, not `"next" not in data`.
**Dependencies**: None

### T2 — Refactor publisher_get
**ID**: T2
**Title**: Use `_fetch_page()` direct for single-item lookup
**Description**: Replace `paginate()` loop with single `_fetch_page()` call. Extract `result["items"][0]` with `[{}]` fallback.
**Files**: `src/datosgob_cli/commands/publisher.py`
**Acceptance**: `publisher get` makes one HTTP request. Returns `{}` on empty result. No pagination loop.
**Dependencies**: T1 (conceptual — uses `_fetch_page` which is unchanged)

### T3 — Add tests with mock
**ID**: T3
**Title**: Mock-based tests for `paginate()` and `publisher_get`
**Description**: 5 test scenarios using `unittest.mock.patch`. Cover happy path, empty result, missing result, last page, and publisher_get.
**Files**: `tests/test_client.py`
**Acceptance**: All pass with `pytest`. No external API calls.
**Dependencies**: T1, T2

### T4 — Integration verification
**ID**: T4
**Title**: Verify real API commands work after fix
**Description**: Run all CLI commands against real datos.gob.es API. Confirm no regressions.
**Files**: (none — manual)
**Acceptance**: `dataset list`, `publisher list`, `theme list`, `spatial list`, `nti list` return real data.
**Dependencies**: T1, T2, T3

---

## Next Step

Ready for `sdd-apply` — single PR, under 400 lines, `decision_needed_before_apply: No`. The orchestrator can proceed directly.