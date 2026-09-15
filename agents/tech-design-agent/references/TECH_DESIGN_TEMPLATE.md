# [STORY-KEY] — [Story short description] — Tech Design

## Instructions for humans

- Resolve every blocking question before approval.
- Confirm assumptions, ownership, sequencing, and rollout expectations.
- Approve only when this design matches the current Jira story and acceptance criteria.
- If the story changes, set the status to `Re-review Required`.

## Instructions for agents

- Read this approved design before making implementation decisions.
- Treat scope, contracts, decisions, risks, and guardrails as constraints.
- Cite relevant sections in implementation plans and handoffs.
- Stop and raise conflicts between this design, the story, and the code.
- Do not silently expand scope or change an approved decision.

---

## Proposed design

High-level proposed design and components to be created or updated.

## Story summary

Describe the user, need, outcome, business value, and boundaries.

## Assumptions for human validation

| ID | human-validation question | Proposed or confirmed assumption | Consequence if changed |
|---|---|---|---|
| Q1 | Question raised during discovery | Answer, proposed default, or `Unresolved` | Affected scope, contract, or behavior |


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


## Decisions and alternatives

| Decision | Choice and rationale | Alternatives considered | Consequences |
|---|---|---|---|
| D1 | Choice | Alternatives | Consequences |

---

## Implementation plan

> This section is written for the plan-auditor and for the developer.
> It must be grounded in the real codebase — every file path and import
> verified before inclusion. Code snippets must compile given the types
> and utilities actually available in the repo.

> **Note for developers:** The guide below is intended to be used as an accelerator. You are still responsible for reviewing and raising questions or concerns if any.

### File manifest

```
[repo-root]/
  [path/to/file]      NEW    — [purpose in one line]
  [path/to/file]      MODIFY — [what changes]
  [path/to/file]      DELETE — [why]
```

### Steps

Follow in order. Each step is independently verifiable.

#### Step 1 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[One sentence describing what this step does and why — do not repeat what was already said above; look ahead to what this step enables.]

```typescript
// [relevant code for this step]
```

---

#### Step 2 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[Description]

```typescript
// code
```

---

*(Add a step for each discrete change. Steps must be ordered by dependency.)*


## Acceptance-criteria traceability

| AC | Components | Implementation steps | Verification |
|---|---|---|---|
| AC1 | Components | Step N | Tests/checks |

