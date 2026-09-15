# STORY-KEY or STORY-SHORT-DESCRIPTION Tech Design - Story summary


## Instructions for humans

- Resolve every blocking question before approval.
- Confirm assumptions, ownership, sequencing, and rollout expectations.
- Approve only when this design matches the current Jira story and acceptance
  criteria.
- If the story changes, set the status to `Re-review Required`.

## Instructions for agents

- Read this approved design before making implementation decisions.
- Treat scope, contracts, decisions, risks, and guardrails as constraints.
- Cite relevant sections in implementation plans and handoffs.
- Stop and raise conflicts between this design, the story, and the code.
- Do not silently expand scope or change an approved decision.


## Assumptions for PO validation

List every product, UX, scope, ordering, ownership, or trade-off question raised during discovery, including questions the PO answered. This section belongs near the top of every design so a PO can validate the decisions before approval. Do not hide a material unanswered question elsewhere in the document.

| ID | PO-validation question | Proposed or confirmed assumption | Consequence if changed |
|---|---|---|---|
| PO1 | Question raised during discovery | Answer, proposed default, or `Unresolved` | Affected scope, contract, or behavior |

## Story summary

Describe the user, need, outcome, business value, and boundaries.

## Scope

### In scope

- Item

### Out of scope

- Item

## Story and acceptance-criteria review

| ID | Requirement or acceptance criterion | Interpretation | Testable? | Gaps or concerns | Design/test obligation |
|---|---|---|---|---|---|
| AC1 | Criterion | Meaning | Yes/No | Finding | Obligation |

## Questions and concerns

### Blocking questions

- None.

### Non-blocking questions

- None.

### Concerns and risks

- None.

## Technical assumptions

| ID | Assumption | Owner | Validation required by |
|---|---|---|---|
| A1 | Assumption | Name/team | Date or milestone |

## Proposed design

Describe the end-to-end behavior, component responsibilities, boundaries,
contracts, and key flows.

## Decisions and alternatives

| Decision | Choice and rationale | Alternatives considered | Consequences |
|---|---|---|---|
| D1 | Choice | Alternatives | Consequences |


### Test strategy

Map unit, integration, contract, end-to-end, performance, security, and
acceptance verification to the affected behavior.

### Rollout and rollback

Describe sequencing, feature flags, compatibility, migration, monitoring,
rollback triggers, and recovery.

## Dependencies and implementation sequence

1. Dependency or implementation step.

## Implementation plan

> This section is written for the plan-auditor and for the developer.
> It must be grounded in the real codebase — every file path and import
> verified before inclusion. Code snippets must compile given the types
> and utilities actually available in the repo.

### File manifest

```
[repo-root]/
  [path/to/file]      NEW — [purpose in one line]
  [path/to/file]      MODIFY — [what changes]
  [path/to/file]      DELETE — [why]
```

### Steps

Follow in order. Each step is independently verifiable.

#### Step 1 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[One sentence describing what this step does and why.]

```typescript
// [relevant code for this step]
```

#### Step 2 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[Description]

```typescript
// code
```

*(Add a step for each discrete change. Steps must be ordered by dependency.)*

### Verify

```bash
# commands to confirm everything compiles, lints, and tests pass
yarn workspace @nextjs-qvc-digital/[package] run check-types
yarn workspace @nextjs-qvc-digital/[package] run test
yarn lint
```

## Acceptance-criteria traceability

| AC | Components | Implementation tasks | Verification |
|---|---|---|---|
| AC1 | Components | Tasks | Tests/checks |

