# Phase 2 — Execute

Take the **Onboarding Plan** (from Phase 1) and implement all **source code,
configuration, changelog, and documentation** changes for the new item type.

> **Prerequisite:** You need the Onboarding Plan. If it is missing, ask for it or
> run Phase 1 first. Trust the plan's verified capabilities; if a value is
> missing or looks wrong, flag it and ask — do not re-derive from scratch.

> **Do NOT touch tests or record cassettes.** Test parametrization
> (`tests/test_commands/conftest.py`) and cassette recording are Phases 3–4
> (Tester). Leave the tree in a state the Tester can pick up.

## Safety rules

- **Never hardcode secrets, tokens, or credentials** in payloads.
- **Use deterministic default content** for payload templates — no real IDs.
- **Validate user-provided parameters** and **raise `FabricCLIError`** with the
  appropriate error code for invalid input (see `errors/` and `fab_constant`).
- **Follow existing patterns** — mirror the closest reference item named in the plan.
- **Maintain alphabetical ordering** in enums and mappings as noted per step.

## How to use the plan

1. Read the plan's Identity, Verified capabilities, Command support decisions, and step list.
2. Execute **only** the steps the plan marks as applicable.
3. After each step, self-verify with the command in the Verification Table.
4. When done, run the validation suite and hand off to the Tester.

## Integration checklist

### Step 1 — Register the Item Type Enum
**File:** `src/fabric_cli/core/fab_types.py`

Add the member to the `ItemType` enum, in the `# API` section, alphabetically:

```python
NEW_ITEM = "NewItem"
```

Member name: `UPPER_SNAKE_CASE`. Value: `PascalCase` matching the API `type` field exactly.

### Step 2 — Add API Format Mapping
**File:** `src/fabric_cli/core/fab_types.py`

```python
# In format_mapping dict:
ItemType.NEW_ITEM: "newItems",
```

Value is the **plural camelCase** REST URL segment: `.../v1/workspaces/{id}/{value}`. Keep alphabetical by member name.

### Step 3 — Add Portal URI Mapping
**File:** `src/fabric_cli/core/fab_types.py`

```python
# In uri_mapping dict:
ItemType.NEW_ITEM: "newitems",
```

Value is the **lowercase** portal slug: `.../groups/{ws_id}/{value}/{item_id}`.

### Step 4 — Add Definition Format Mapping (if the item has definitions)
**File:** `src/fabric_cli/core/fab_types.py`

```python
# In definition_format_mapping dict:
ItemType.NEW_ITEM: {"default": ""},
```

`"default"` is required. Add extra keys for named formats (e.g., `"TMDL": "?format=TMDL"`). Skip if no definition support.

### Step 5 — Add OneLake Folders (if applicable)
**File:** `src/fabric_cli/core/fab_types.py`

Only if the plan lists OneLake folders. Add a folders `Enum`, an entry in
`ItemFoldersMap`, and — for writable folders — an entry in
`ItemOnelakeWritableFoldersMap`:

```python
class NewItemFolders(Enum):
    TABLES = "Tables"
    FILES = "Files"

# ItemFoldersMap:
ItemType.NEW_ITEM: [folder.value for folder in NewItemFolders],
```

### Step 6 — Add Job Type Mapping (if applicable)
**File:** `src/fabric_cli/core/fab_types.py`

Only if the plan says jobs are supported. Use the **exact** job type string from the plan:

```python
class FabricJobType(Enum):
    NEW_JOB = "NewJobType"

# ITJobMap:
ItemType.NEW_ITEM: FabricJobType.NEW_JOB,
```

### Step 7 — Add Creation Parameters (if applicable)
**File:** `src/fabric_cli/utils/fab_cmd_mkdir_utils.py`

In `get_params_per_item_type()`:

```python
case ItemType.NEW_ITEM:
    required_params = ["paramA"]
    optional_params = ["paramB"]
```

### Step 8 — Add Creation Payload Logic (if applicable)
**File:** `src/fabric_cli/utils/fab_cmd_mkdir_utils.py`

In `add_type_specific_payload()`, add a case using the pattern that matches the plan:

```python
case ItemType.NEW_ITEM:
    # A: inline base64 definition
    payload_dict["definition"] = {"parts": [{
        "path": "content.json",
        "payload": "<base64-encoded-default-content>",
        "payloadType": "InlineBase64",
    }]}
    # B: file-based template  -> create src/fabric_cli/commands/fs/payloads/Blank.NewItem/
    # C: creationPayload (shell-only): payload_dict["creationPayload"] = {...}
```

If using option B, create `src/fabric_cli/commands/fs/payloads/Blank.NewItem/` with deterministic template files.

### Step 9 — Add Import Payload Handling
**File:** `src/fabric_cli/core/hiearchy/fab_item.py`

In `get_payload()`, add the item type. **Standard** items join the existing multi-case match:

```python
case (
    ItemType.REPORT
    | ...
    | ItemType.NEW_ITEM
):
    return {
        "type": str(self.item_type),
        "folderId": self.folder_id,
        "displayName": self.short_name,
        "definition": definition,
    }
```

Use a dedicated case only for format-specific handling.

### Step 10 — Update Command Support Configuration
**File:** `src/fabric_cli/core/fab_config/command_support.yaml`

Apply exactly the **Command support decisions** from the plan. Use `snake_case`
names and maintain alphabetical order.

- **10a. `unsupported_items` (always review):** add the item to `rm`, `get`,
  `set`, and/or `mkdir` `unsupported_items` for any command the API does **not** support.
- **10b. `export`** supported_items — if Get Definition is supported.
- **10c. `import`** supported_items — if create-with-definition is supported (else add to `import.unsupported_items`).
- **10d. `mv`** supported_items — if both export and import are supported.
- **10e. `cp`** supported_items — if both export and import are supported.

### Step 11 — TESTS (SKIP — Tester's responsibility)
**Do not edit `tests/test_commands/conftest.py` and do not record cassettes.**
Leave a note in your hand-off so the Tester knows which lists to update.

### Step 12 — Add Changelog Entry
Preferred — run changie (valid kinds include `new-items`):

```bash
changie new --kind new-items --body "Add support for NewItem item type" --custom Author=<github-username>
```

Or create `.changes/unreleased/new-items-YYYYMMDD-HHMMSS.yaml`:

```yaml
kind: new-items
body: Add support for NewItem item type
time: 2026-01-15T10:30:00.000000000Z
custom:
    Author: <github-username>
    AuthorLink: https://github.com/<github-username>
```

### Step 13 — Update Documentation Pages
- **13a.** `docs/essentials/resource_types.md` — add a `.NewItem` row to the Item Types table (alphabetical).
- **13b.** `docs/examples/item_examples.md` — add `.NewItem` to the copy list (if `cp`) and export list (if `export`).

## Verification Table

Replace `NEW_ITEM`/`NewItem`/`new_item` with the real values.

| Step | Verify with | When |
|------|-------------|------|
| 1. Enum | `grep -n 'NEW_ITEM.*=.*"NewItem"' src/fabric_cli/core/fab_types.py` | Always |
| 2. format_mapping | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/fab_types.py` | Always |
| 3. uri_mapping | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/fab_types.py` | Always |
| 4. definition_format | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/fab_types.py` | Has definitions |
| 5. OneLake folders | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/fab_types.py` | Has folders |
| 6. Job mapping | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/fab_types.py` | Has jobs |
| 7/8. Creation params/payload | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/utils/fab_cmd_mkdir_utils.py` | Has params |
| 9. Import payload | `grep -n 'ItemType.NEW_ITEM' src/fabric_cli/core/hiearchy/fab_item.py` | Always |
| 10. Command support | `grep -n 'new_item' src/fabric_cli/core/fab_config/command_support.yaml` | Always |
| 12. Changelog | `ls .changes/unreleased/ \| grep -i newitem` | Always |
| 13a. Resource types | `grep -n 'NewItem' docs/essentials/resource_types.md` | Always |
| 13b. Item examples | `grep -n 'NewItem' docs/examples/item_examples.md` | Has cp/export |
| Type/format checks | `black src/ && mypy src/ --ignore-missing-imports` | Always |

## Hand-off

When your steps pass, tell the user which files changed and which conftest
parametrization lists the Tester still needs to update (from the plan's Test
step list). The **tests are not yet updated or recorded** — that is Phases 3–4.
