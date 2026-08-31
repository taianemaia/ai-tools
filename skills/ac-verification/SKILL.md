---
name: ac-verification
description: >
  For developers and tech leads: verifies whether a user story's acceptance
  criteria are actually implemented and tested, as a gate before moving the
  story to "test ready." Checks each AC against the code — implementation,
  test coverage, and citation accuracy — and reports status per AC. Use
  whenever someone asks "is this story done", "check if all ACs have been
  fulfilled", "verify the acceptance criteria before QA", "can we move this
  to test ready", or pastes a story with an AC list and wants it checked off
  by a dev.
---

# AC verification (dev / tech lead gate)

You are a developer or tech lead confirming a story's acceptance criteria are genuinely met before
the story moves to "test ready," by checking them against the code. This is not the QA-facing test
plan, and this skill does not determine how each AC will be tested — only whether it's implemented.

## Guardrails

- **No invented requirements.** Verify exactly the ACs as written. Do not add extra checks, edge
  cases, or expectations the story doesn't state, no matter how reasonable they seem. If you think
  something is missing from the story itself, say so as a separate observation — don't fold it into
  the AC table as if it were part of the requirement.

- **No invented ACs.** If the story has no explicit acceptance criteria list, stop and tell the
  human. Do not infer, paraphrase, or synthesize ACs from the story's prose or your own judgment —
  ask them to provide the AC list before proceeding.

## Step 1 — Get the story and its ACs

Get the story text and its acceptance criteria list from the user. That's all — do not go looking
for requirements anywhere else. If the user hasn't provided an AC list, stop and ask for it per the
guardrail above.

## Step 2 — Verify each AC against the code

For each AC:

1. Find the implementation. Read it, don't infer from a function name.

2. Find a unit test and, if applicable, an integration/e2e test that exercises this exact behavior.
   If no integration test exists but the AC is the kind of behavior integration tests are well
   suited to verify (spans multiple layers/components, depends on real request/response wiring,
   etc.), flag that as a coverage gap worth considering — separate from the AC's status below.

3. **Verify every citation before writing it down** — `grep -n` the exact string and confirm the
   line number. A wrong line number in a sign-off doc is worse than no citation.

4. Mark status precisely: **Met** (implemented + tested), **Partially met**, or **Not met**.

- **Additional verification sources.** The user may provide additional sources, such as technical design documents. If they do, read those documents and compare them with the implementation and stated ACs. Use only sources the user explicitly identifies; do not look for or infer additional requirements. Report any mismatch as a separate observation, not as a new AC.

## Step 3 — Present the assessment

Reply with the assessment as inline markdown, following the structure in
`references/output-format.md` — do not write it to a file.
