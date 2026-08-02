# Phase 4 — Record cassettes and validate

Tests run in **playback mode** by default (using recorded cassettes). To cover a
new item type you record new cassettes in **live mode**, then verify playback
passes with no live calls.

## Safety rules

- **Recording privacy:** before committing recordings, confirm **no private
  information** is present in the cassette `.yaml` files. If private data was
  captured, mask/mock it via the test processors (`tests/test_commands/processors.py`).
- **Never fabricate cassettes by hand.** Cassettes under
  `tests/test_commands/recordings/` must be produced by running the tests in
  record mode against a real environment.
- **Do not ask for secrets through chat.** If a variable holds a secret, instruct
  the user to `export` it in their own terminal. Never request or echo secret values.

## Step B — Record the cassettes

`--record` sets the VCR `record_mode` to `all` and re-records matching cassettes:

```bash
# Record a single test file (live calls to Fabric)
python3 -m pytest tests/test_commands/test_get.py --record

# Record the specific tests that now cover the new item type (faster, targeted)
python3 -m pytest tests/test_commands/test_export.py -k "new_item or NEW_ITEM" --record
```

Cassettes are written to
`tests/test_commands/recordings/<parent_folder>/<test_file>/<test_name>.yaml`.

**Recommended recording order** (record the suites the plan enabled):

1. `test_cd.py`, `test_ls.py`, `test_exists.py` — navigation/listing (from `ALL_ITEM_TYPES`)
2. `test_mkdir.py` / creation — if `mkdir` is supported
3. `test_get.py`, `test_set.py` — metadata
4. `test_export.py`, `test_import.py` — if definition support
5. `test_cp.py`, `test_mv.py` — if `cp`/`mv` are supported
6. `test_rm.py` — deletion (run last; it cleans up created items)

## Step C — Environment variables required for recording

**Recording gate:** recording makes **real** calls to Microsoft Fabric. Tell the
user which environment variables to set and confirm they are set + they are
authenticated to a live environment **before** running `--record`.

### Always required to record item tests

| Variable | Purpose |
|----------|---------|
| A valid Fabric login | The CLI must be authenticated (`fab auth login` or a service principal). |
| `FABRIC_CLI_TEST_CAPACITY_ID` | Real capacity GUID — needed to create the workspace/items. |
| `FABRIC_CLI_TEST_CAPACITY_NAME` | Real capacity name. |

### Conditionally required (based on the item's capabilities)

| Variable(s) | When needed |
|-------------|-------------|
| `FABRIC_CLI_TEST_ADMIN_UPN`, `FABRIC_CLI_TEST_ADMIN_ID` | ACL/admin-related item operations |
| `FABRIC_CLI_TEST_USER_UPN`, `FABRIC_CLI_TEST_USER_ID` | Access-control tests |
| `FABRIC_CLI_TEST_SERVICE_PRINCIPAL_ID` | SPN-based auth scenarios |
| `FABRIC_CLI_TEST_SQL_SERVER`, `FABRIC_CLI_TEST_SQL_DATABASE` | Items that connect to SQL (e.g., mirrored/DB items) |
| `FABRIC_CLI_TEST_AZURE_SUBSCRIPTION_ID`, `FABRIC_CLI_TEST_AZURE_RESOURCE_GROUP`, `FABRIC_CLI_TEST_AZURE_LOCATION` | Items with Azure resource dependencies |
| Connection/gateway vars (`FABRIC_CLI_TEST_CREDENTIAL_DETAILS_*`, `FABRIC_CLI_TEST_ONPREMISES_GATEWAY_*`) | Items that require a connection or gateway |

> **Determine the exact subset** from the plan's Verified capabilities. If the
> item has no external dependencies, capacity + auth is usually enough. When a
> recording fails with an auth/validation error, the failing request in the
> traceback tells you which resource (and thus which variable) is missing — see
> `tests/authoring_tests.md` for the full variable reference and mock-first guidance.

Example (non-secret) setup the user runs in their shell:

```bash
export FABRIC_CLI_TEST_CAPACITY_ID="<real-capacity-guid>"
export FABRIC_CLI_TEST_CAPACITY_NAME="<real-capacity-name>"
```

## Step D — Verify and hand back

```bash
# Playback must pass without touching the network
python3 -m pytest tests/test_commands/ -k "new_item or NEW_ITEM"

# Formatting / typing
black tests/ && mypy tests/ --ignore-missing-imports
```

### Verification Table

| Item | Verify with |
|------|-------------|
| Cassettes recorded | `ls tests/test_commands/recordings/**/ \| grep -i new_item` |
| Playback passes | `python3 -m pytest tests/test_commands/ -k "new_item or NEW_ITEM"` |

When everything passes, confirm to the user that the parametrization lists were
updated, cassettes were recorded and scrubbed of private data, and playback
passes with no live calls. Remind them to review the recorded `.yaml` files in
the diff before opening a PR.
