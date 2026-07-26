# Phase 1 — Plan

Gather everything needed to onboard a new Fabric item type, **verify each
capability against the official Fabric REST API documentation**, and produce a
single, unambiguous **Onboarding Plan** (template in [SKILL.md](../SKILL.md)).

> **Do not write source code, tests, or config in this phase.** The only output
> is the Onboarding Plan and answers to the user's questions.

> **If you are unsure about any detail** — the API URI, portal slug, whether the
> item supports definitions, OneLake folders, jobs, or which commands are
> supported — **verify it against the API docs first, and if still unclear, ask
> the requestor before finalizing the plan.**

Do not produce the plan until Gather + Verify + Classify are complete.

## Phase A — Gather

Collect the following. You only strictly need the **display name** to start;
derive or verify the rest during Phase B.

| Information | Example | How to obtain |
|-------------|---------|---------------|
| **Display name** (PascalCase, matches API `type`) | `Map` | Ask the requestor |
| **API plural URI segment** | `maps` | Verify in API docs (Phase B) |
| **Portal URI slug** | `maps` | Ask requestor / open item in portal |
| **Has definition/payload** | Yes / No | Verify in API docs (Phase B) |
| **Definition formats** | `ipynb`, `TMDL` | Verify in API docs |
| **OneLake folders** | `Tables`, `Files` | Ask requestor (varies per type) |
| **Supports jobs** | Yes / No | Verify in API docs |
| **Job type name** | `RunNotebook` | Verify in API docs (must match exactly) |
| **Creation parameters** | `enableSchemas` | Verify in Create endpoint docs |

## Phase B — Verify capabilities against the Fabric REST API docs (REQUIRED)

The set of commands the CLI enables for an item type is driven **directly** by
which REST APIs the item supports. You **must fetch the actual API pages** — do
not infer capabilities from the item name alone.

### B1. Fetch the item's Operations page

```
https://learn.microsoft.com/en-us/rest/api/fabric/{itemtype-lowercase}/items
```

where `{itemtype-lowercase}` is the PascalCase display name lowercased with no
separators (e.g., `DataPipeline` → `datapipeline`, `KQLDatabase` → `kqldatabase`,
`GraphQLApi` → `graphqlapi`).

- If the URL 404s, try alternate spellings, then fall back to the
  [Fabric REST API root](https://learn.microsoft.com/en-us/rest/api/fabric/) and
  navigate to the item's section. If still inaccessible, ask the requestor to
  paste the operations list.

From the **Operations** table, record which of these exist:

| API operation | Present? |
|---------------|----------|
| Create Item (`POST .../items`) | ☐ |
| Delete Item (`DELETE .../items/{id}`) | ☐ |
| Get Item (`GET .../items/{id}`) | ☐ |
| Update Item (`PATCH .../items/{id}`) | ☐ |
| List Items (`GET .../items`) | ☐ |
| **Get [Item] Definition** (`POST .../getDefinition`) | ☐ |
| **Update [Item] Definition** (`POST .../updateDefinition`) | ☐ |
| Create with Definition (`POST .../items` accepts a `definition` body) | ☐ |
| Jobs / Run on demand (`POST .../jobs/instances`) | ☐ |

### B2. Fetch the Create endpoint page

```
https://learn.microsoft.com/en-us/rest/api/fabric/{itemtype-lowercase}/items/create-{item-type-kebab-case}
```

- `{item-type-kebab-case}` inserts hyphens between PascalCase words and
  lowercases: `DataPipeline` → `create-data-pipeline`, `KQLDatabase` →
  `create-kql-database`.
- Confirm whether the request body accepts a `definition` (full definition
  support) or only metadata / a `creationPayload` (shell-only, like
  `Warehouse`/`Lakehouse`).
- Note any **required** vs **optional** creation parameters in the request body.

> **Nuance:** Some pages explicitly state "This API does not support item
> definition." Treat those as shell-only. When definition support is ambiguous,
> present your findings and ask the requestor to confirm before finalizing.

### B3. Map API support → CLI commands

Translate the verified operations into `command_support.yaml` decisions:

| Verified API capability | CLI effect (in `command_support.yaml`) |
|-------------------------|----------------------------------------|
| Get Definition | Add to `export` supported_items |
| Create-with-definition | Add to `import` supported_items |
| Get Definition **and** Create-with-definition (and Update Definition) | Add to `mv` **and** `cp` supported_items |
| No Delete Item API | Add to `rm` → `unsupported_items` |
| No Get Item API | Add to `get` → `unsupported_items` |
| No Update Item API | Add to `set` → `unsupported_items` |
| No Create Item API | Add to `mkdir` → `unsupported_items` |
| No Create-with-definition (but shell create exists) | Add to `import` → `unsupported_items` |

**Rules of thumb:**
- `mv` and `cp` require **both** export (getDefinition) **and** import
  (create-with-definition), because they export from source and import to destination.
- `export` may include items that support getDefinition but not import/mv/cp.
- Use `snake_case` for the item name in the YAML (e.g., `semantic_model`, `data_pipeline`, `copy_job`).

## Phase C — Classify complexity

Use the verified capabilities to pick the item's category. This tells the
Implementer and Tester which steps apply.

| Category | Characteristics | Reference items |
|----------|-----------------|-----------------|
| **Simple** | No definition, no params, no folders, no jobs | `Dashboard`, `Datamart` |
| **Definition support** (most common) | export/import/mv/cp, no creation params | `Map`, `CopyJob`, `Dataflow`, `GraphQLApi`, `UserDataFunction` |
| **Creation parameters** | Requires params at create time | `Lakehouse` (enableSchemas), `Warehouse`, `KQLDatabase` |
| **OneLake folders** | Exposes `Tables`/`Files`/etc. | `Lakehouse`, `Warehouse`, `KQLDatabase` |
| **Job support** | Supports on-demand jobs | `Notebook`, `DataPipeline`, `SparkJobDefinition` |
| **Full-featured** | All of the above | `Notebook` |

**Existing item types to study** (point the Implementer/Tester at the closest match):

| Item Type | Enum | Good reference for |
|-----------|------|--------------------|
| `Dashboard` | `DASHBOARD` | Minimal integration |
| `Map` | `MAP` | Definition support, no params/jobs/folders |
| `Lakehouse` | `LAKEHOUSE` | Creation params, OneLake folders, jobs |
| `Notebook` | `NOTEBOOK` | Definitions, jobs, custom payload |
| `SemanticModel` | `SEMANTIC_MODEL` | Definition formats (TMDL/TMSL) |
| `Report` | `REPORT` | Dependency creation (auto-creates SemanticModel) |
| `MirroredDatabase` | `MIRRORED_DATABASE` | Multiple payload variants |
| `MountedDataFactory` | `MOUNTED_DATA_FACTORY` | Required params, custom payload |

## Output

Fill in every field of the **Onboarding Plan** template in [SKILL.md](../SKILL.md)
with **verified** values, present it in chat, and offer to save it under
`.github/skills/onboard-item-type/plans/`. Then hand off to the Implementer
(Phase 2) and Tester (Phases 3–4).
