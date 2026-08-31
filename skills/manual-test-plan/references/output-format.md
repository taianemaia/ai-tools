# TICKET-KEY — Story summary: Manual Test Plan

## Prerequisites

Test data necessary, environment access, tools access (e.g. Saucelabs) and any tool setup (e.g. Postman environment variables) needed before running any test case.

1. <Prerequisite step>

## Test cases

One block per QA-testable AC, in the order the ACs were provided.

### TC<N> — <AC text or short title>

**Steps**

1. <Step>

**Expected result**

<Exact, directly observable expected result — a response field value, a status code, a visible element>

- [ ] Pass / Fail

## Not testable by QA — requires a tech lead

Include only if at least one AC requires tech-lead verification. Never drop a non-testable AC
silently — every excluded AC must appear here.

| AC | Reason tech-lead access is required | Local reproduction steps (self-verified) | Result observed |
|---|---|---|---|
| <AC> | <Reason> | <Exact steps actually run> | <Observed result, or "not reproducible — <why>"> |

## Sign-off

- [ ] All QA-testable test cases pass.
- [ ] Every "Not testable by QA" AC has either a verified local reproduction result or an explicit
      statement that none could be found.

## QA Observations
<Any observations to be shared by QA or tech lead>
