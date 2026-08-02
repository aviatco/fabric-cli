# Phase 3 — Test (parametrization)

After the Implementer has landed the source/config/docs changes, make the test
suite cover the new item type by adding it to the parametrization lists.

> **Prerequisite:** You need the Onboarding Plan and the Implementer's changes
> already applied. If the source changes are missing, tests will fail — confirm
> with the user before proceeding to recording (Phase 4).

## Safety rules

- **Never hardcode secrets, tokens, or credentials** in tests.
- **Use deterministic test data** — no real tenant IDs, workspace IDs, or user emails.

## Update the parametrization lists

**File:** `tests/test_commands/conftest.py`

Add the new item type to the parametrized lists so existing tests cover it. Only
touch the lists indicated by the plan's Command support decisions.

### A1. `ALL_ITEM_TYPES` (always)
Drives the comprehensive suite (cd, ls, exists, rm, get, set, mkdir).

```python
ALL_ITEM_TYPES = [
    ...
    ItemType.NEW_ITEM,    # add at the end
]
```

### A2. `basic_item_parametrize` (basic items only)
Add **only if** the item has no special creation params, no OneLake folders, and
no special properties (i.e., it is NOT in
`mkdir_item_with_creation_payload_success_params` or
`get_item_with_properties_success_params`).

### A3. `mv_item_to_item_success_params` and `mv_item_within_workspace_rename_success_params` (if `mv` is supported)

### A4. `get_item_with_properties_success_params` (if the item has extended `fab get -v` properties)

```python
(ItemType.NEW_ITEM, ["properties", "someSpecificProperty"]),
```

### A5. Export lists (if `export` is supported)
Add to all export parametrizations with the correct expected values:

```python
(ItemType.NEW_ITEM, ".json"),   # export_item_with_extension_parameters
ItemType.NEW_ITEM,              # export_item_types_parameters
(ItemType.NEW_ITEM, 2),         # export_item_default_format_parameters (expected file count)
(ItemType.NEW_ITEM, ".txt"),    # export_item_invalid_format_parameters
```

### A6. `set_item_metadata_for_all_types_success_item_params` (if `set` is supported)

## Verification Table

| Item | Verify with |
|------|-------------|
| `ALL_ITEM_TYPES` | `grep -n 'NEW_ITEM' tests/test_commands/conftest.py` |
| `basic_item_parametrize` | `grep -n 'NEW_ITEM' tests/test_commands/conftest.py` |
| mv params | `grep -n 'NEW_ITEM' tests/test_commands/conftest.py` |
| export params | `grep -n 'NEW_ITEM' tests/test_commands/conftest.py` |

Once the lists are updated, proceed to [record.md](record.md) to record the
cassettes, then validate playback.
