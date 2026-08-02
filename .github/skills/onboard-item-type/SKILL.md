---
name: onboard-item-type
description: Onboard a new Microsoft Fabric item type into the Fabric CLI (fab). Activate when a contributor asks to add, support, integrate, or onboard a new Fabric item type (e.g., "add support for DataActivator", "onboard the Map item type", "wire up a new Fabric item"). Covers planning capabilities against the Fabric REST API docs, implementing source/config/docs changes, and updating + recording the tests.
---

# Onboard a New Fabric Item Type

This skill packages everything needed to add a new Microsoft Fabric **item type**
to the Fabric CLI. It is **role-agnostic**: the Planner, Implementer, and Tester
agents each load the reference file for their phase and follow it.

The work is organized into four phases sharing one contract — the **Onboarding
Plan** produced in Phase 1 and consumed by every later phase.

| Phase | Reference | Owner role | Purpose |
|-------|-----------|-----------|---------|
| 1. Plan | [references/plan.md](references/plan.md) | Planner | Verify capabilities against the Fabric REST API docs and produce the Onboarding Plan. |
| 2. Execute | [references/execute.md](references/execute.md) | Implementer | Apply source, config, changelog, and docs changes. |
| 3. Test | [references/test.md](references/test.md) | Tester | Add the item type to the test parametrization lists. |
| 4. Record | [references/record.md](references/record.md) | Tester | Record VCR cassettes against a live Fabric environment. |

## How to use this skill

1. Identify your phase from the role you are running as (or the step the user asks for).
2. Open the matching reference file and follow it **step by step**.
3. Keep the **Onboarding Plan** as the single source of truth — do not re-derive
   API capabilities that the plan already verified.
4. Execute **only** the steps the plan marks as applicable to this item type.

## Safety rules (all phases)

- **Never hardcode secrets, tokens, or credentials**, and never request secrets through chat.
- **Use deterministic, non-real values** — no real tenant IDs, workspace IDs, or user emails.
- **Verify, don't guess.** Every capability must trace to an API doc page or an explicit answer from the requestor.
- **Follow existing patterns** — mirror the closest reference item and preserve alphabetical ordering where required.
- **Never fabricate cassettes.** Recordings must come from running the tests against a real environment.

## Onboarding Plan template

The Planner emits this block; every later phase reads it. Save it to
`.github/skills/onboard-item-type/plans/<name>.plan.md` if you want to persist it.

```markdown
# Onboarding Plan — <DisplayName>

## Identity
- Display name (API `type`): <PascalCase>
- Enum member: <UPPER_SNAKE_CASE>
- snake_case name (for YAML/tests): <snake_case>
- API plural URI segment (format_mapping): <camelCasePlural>
- Portal URI slug (uri_mapping): <lowercaseslug>

## Verified capabilities (cite the API doc URLs you fetched)
- Create / Delete / Get / Update Item: yes/no each
- Get Definition / Update Definition / Create-with-definition: yes/no each
- Definition formats: <list or n/a>
- OneLake folders: <list or none> (writable: <list or none>)
- Jobs: yes/no — job type name: <exact API string or n/a>
- Creation params: required=<list>, optional=<list> (or none)
- Source of truth: <API doc URLs>

## Classification
- Category: <Simple | Definition support | Creation params | OneLake folders | Job support | Full-featured>
- Closest existing reference: <e.g., Map>

## Command support decisions (command_support.yaml)
- export / import / mv / cp: yes/no each
- rm / get / set / mkdir unsupported_items: add? yes/no each

## Applicable step list
- Execute steps: <e.g., 1-4, 9, 10, 12, 13>
- Test lists to touch: <which conftest parametrizations>
- Recording env vars needed: <subset>

## Open questions / assumptions
<anything unverifiable that the requestor must confirm>
```
