# AC verification — output format

Reply inline as markdown, structured exactly as below. Do not write this to a file.

## AC assessment

| AC | Status | Implementation evidence | Test evidence | Notes |
|---|---|---|---|---|
| <AC text or number> | Met / Partially met / Not met | `path/to/file.ts:LINE` — what it does | `path/to/file.spec.ts:LINE` — what it asserts | coverage gaps or caveats specific to this AC |

One or multiple rows per AC, in the order the user provided them. Every evidence citation must be a real,
grep-verified file path and line number — never approximate.

## Integration-test coverage gaps

Include only if at least one applies. One line per AC:

- `<AC>` — no integration/e2e test exists for this behavior, though it [spans multiple
  layers/components / depends on real request-response wiring / etc.] and would benefit from one.

## Additional-source mismatches

Include only if the user provided additional verification sources (e.g. a tech design doc) and the
implementation or ACs don't match them:

- `<source>` says X, but the implementation/AC does Y — reported as a mismatch, not a new AC.

## Story observations

Include only if applicable. Anything that seems missing or ambiguous in the story itself, kept
separate from the AC table since it isn't a stated requirement:

- <observation>
