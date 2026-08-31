---
name: manual-test-plan
description: >
  For QA or a technical tester: produces a step-by-step manual test guide
  for a user story's acceptance criteria, to run against a real,
  already-integrated environment (the tester has real access to the running
  application and can call its APIs, e.g. via Postman — no local stubs or
  fake upstreams). Triages each AC as QA-testable this way, or as requiring
  a tech lead to verify locally (e.g. runtime changes like hardcoded URLs,
  env var overrides, or a local mock server to force a timeout/fallback
  path) — for the latter, works out and self-verifies a concrete local
  reproduction, then lists it separately with the reason, for human review.
  Use whenever someone asks to "create a manual test plan", "write a test
  guide for QA", "how do we test these ACs", or a story is ready to hand to
  a tester.
---

# Manual test plan (QA / technical tester facing)

You are writing a guide for someone testing a story against a real environment — not reviewing the
code yourself. The tester has genuine access to a running, already-integrated instance of the
application (real upstreams, real data they can author through normal means) and a tool like
Postman to call its APIs. They do not change code, environment variables, or infrastructure to test.

## Guardrail: no invented requirements

Write test cases only for what the story's acceptance criteria literally state. Don't add extra
scenarios, edge cases, or pass/fail criteria the story doesn't ask for — even ones that seem like
good practice. Designing sufficient *test data* to make a real AC's assertion produce a
distinguishable result (Step 3 below) is expected; inventing *additional requirements* is not.

## Step 1 — Get the AC list and triage each AC

Get the story's acceptance criteria from the user, verbatim — same guardrail as above.

For each AC, ask: **can this be verified purely by using the live application or calling its API,
with no code, environment-variable, or infrastructure changes?** QA testers have real access to the
application in an integrated environment — they can drive the UI, call APIs directly, and author
test data through normal, exposed means.

Mark it **"Requires tech lead"** instead when verifying it needs something QA cannot do through
normal application access — for example:
- Hardcoding or overriding a URL/host to point at a controlled endpoint
- Changing an environment variable and restarting the service
- Standing up a local mock/stub to force a dependency into a specific failure mode (timeout,
  5xx, slow response) that can't be reliably triggered against a real upstream on demand
- Manipulating the system clock or a feature flag with no exposed toggle
- Reading internal logs, metrics, or process state not visible from outside the application

Judge by what verifying the behavior actually requires, not by what's more convenient to write
about. Record a one-line reason for every "Requires tech lead" AC.

## Step 2 — Set the environment and tool before drafting anything

- **Environment.** Default to **INT1** unless the user has explicitly stated a different
  environment. Don't ask — state which environment the plan targets and proceed.
- **Tool.** Don't ask the user which tool they'll use. Suggest one yourself — state which tool and
  why (e.g. Postman, because it lets the tester toggle a header on/off without retyping it) —
  unless the user has already told you explicitly which tool to use, in which case use that one.
  Match the plan's instructions to whichever tool applies (e.g. Postman: environment variables, a
  Headers-tab checkbox to toggle a header without retyping it; a UI: click-by-click navigation).

Assume real access to a real environment by default — do not propose a local stub, a mock server,
or a fake upstream for the QA-testable test cases in Step 3. Local workarounds only belong in
Step 4, for ACs a tech lead must verify instead of QA.

## Step 3 — Write one test case per QA-testable AC

For each AC marked QA-testable in Step 1:
- State any test data that needs to exist first, and how to create it through normal means in the
  real environment (e.g. author real content with specific fields via the system this repo
  integrates with) — not synthetic data injected some other way.
- Give exact steps: request method/URL/headers, or exact UI actions.
- Give the exact expected result, in terms the tester can directly observe (a response field value,
  a visible element, a status code).
- Before finalizing, walk through the expected result by hand for every branch the AC implies (e.g.
  if an AC claims two conditions produce different outcomes, confirm your chosen test data actually
  makes them differ — a coincidentally-symmetric example proves nothing).
- End with a Pass/Fail checkbox.

## Step 4 — For each "Requires tech lead" AC, work out a local repro and list it separately

Do not write a QA test case for these, and do not invent a workaround so QA can "sort of" test them
in the real environment. Instead:

1. Design a concrete, minimal local reproduction: exact env vars to set, exact commands to run,
   exact steps to force the condition.
2. **Actually run it** and confirm it reproduces or validates the behavior — "self-verified" means
   executed, not theorized.
3. If you can't find a way to reproduce it locally either, don't paper over that — say so plainly
   instead of writing repro steps that weren't actually confirmed.

List each of these ACs in a clearly separate section of the document, e.g. **"Not testable by QA —
requires a tech lead"**, with:
- The AC itself
- The concrete reason it requires tech-lead-level access
- The self-verified local reproduction steps and the result observed when you ran them (or, if none
  could be found, a plain statement of that)

This section exists so a human reviewing the plan can see exactly what's excluded from QA testing
and why — never drop a non-testable AC silently, and never hand QA a test case for something they
structurally cannot verify.

## Step 5 — Produce the document

Follow this repo's existing `docs/` naming convention. Write `<TICKET>_MANUAL_TEST_PLAN.md`
containing: prerequisites for the confirmed environment/tool, one test case per QA-testable AC, the
"Not testable by QA" section for the rest, and a sign-off checklist.

## Step 6 — Final sweep

After any edit that removes a test case or a flagged AC, grep the document for the removed term to
confirm nothing was left behind.
