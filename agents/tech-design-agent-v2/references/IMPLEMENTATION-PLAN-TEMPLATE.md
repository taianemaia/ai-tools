# [STORY-KEY] — Implementation Plan

> **<u>Note for developers:</u>** The guide below is intended to be used as an accelerator. You are still the responsible for reviewing and raising questions/concerns, if any.

## File manifest

```
[repo-root]/
  [path/to/file]      NEW    — [purpose in one line]
  [path/to/file]      MODIFY — [what changes]
  [path/to/file]      DELETE — [why]
```

---

## Steps

Follow in order. Each step is independently verifiable.

### Step 1 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[One sentence describing what this step does and why - Do not add details previously discussed, look ahead.]

```typescript
// [relevant code]
```

---

### Step 2 — [Short verb phrase]

**File:** `[exact/path/to/file.ts]` *(new | modify)*

[Description]

```typescript
// [relevant code]
```

---

*(Duplicate the step block above for each discrete change. Steps must be ordered by dependency.)*

---

## Acceptance-criteria traceability

| AC  | Components  | Implementation steps | Verification    |
| --- | ----------- | -------------------- | --------------- |
| AC1 | [Component] | Step N               | [Test or check] |
| AC2 | [Component] | Step N               | [Test or check] |

---

## Dependencies and blockers

| Item                         | Type                  | Blocking? | Owner            |
| ---------------------------- | --------------------- | --------- | ---------------- |
| [Dependency or prerequisite] | Story / PR / decision | Yes / No  | [Team or person] |
