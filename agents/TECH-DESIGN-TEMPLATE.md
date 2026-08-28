# STORY-KEY Tech Design - Story summary

## Document control

| Field | Value |
|---|---|
| Status | Proposed |
| Jira story | [STORY-KEY](JIRA-URL) |
| Confluence page | Not published |
| Design owner | Name |
| Requester/approver | Name |
| Approval date | Not approved |
| Story snapshot date | YYYY-MM-DD |
| Story revision/hash | Revision ID or SHA-256 of normalized story and ACs |

## Instructions for humans

- Resolve every blocking question before approval.
- Confirm assumptions, ownership, sequencing, and rollout expectations.
- Approve only when this design matches the current Jira story and acceptance
  criteria.
- For a story with user-visible frontend impact, review and select the UI
  mockups before approving the complete design.
- If the story changes, set the status to `Re-review Required`.

## Instructions for agents

- Read this approved design before making implementation decisions.
- Treat scope, contracts, decisions, risks, and guardrails as constraints.
- Cite relevant sections in implementation plans and handoffs.
- Stop and raise conflicts between this design, the story, and the code.
- Do not silently expand scope or change an approved decision.
- When UI design is required, use the selected Confluence attachments as visual
  constraints. Do not substitute unreviewed layouts or commit design artifacts.

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

## Mockups and design artifacts

Use this section whenever a design has user-visible UI or produces a visual,
diagram, prototype, export, or other binary review artifact. For user-visible
designs, this section is required: inventory the selected mockup set, its
states, its local location and checksum when a local copy exists, and its
Confluence status.
Keep it for future iterations even when the first upload is manual.

For Product Design exploration, generate candidates inside this repository at
`.design-artifacts/<JIRA-KEY>/candidates/`, never in a chat or system temporary
directory. After requester selection, retain the final state set under
`.design-artifacts/<JIRA-KEY>/`: move selected files out of `candidates/`, then
delete `candidates/` with all rejected files. Both locations are Git-ignored.
Record a local location only when retained final assets actually exist. Never
commit generated images, Figma exports, prototypes, archives, or design-QA
files; commit only this inventory and iteration history.

| Artifact | Viewport/state | Local location/checksum | Confluence status/link |
|---|---|---|---|
| `<KEY>-ui-01-state.png` | Desktop/state | Not retained locally / checksum unavailable | Pending upload |

### Manual upload instructions

1. Attach every selected artifact to the story's Confluence Tech Design page.
2. Record the Confluence attachment link, or `Published — URL pending` when
   publication is confirmed but the URL has not yet been supplied.
3. Record the upload date and completion status in the iteration log.
4. Confirm each attachment opens for the intended audience before implementation
   handoff.
5. Keep local binary files Git-ignored and uncommitted. On confirmed selection,
   move selected files to the artifact root, delete `candidates/`, and update
   this section.

Only selected final artifacts are attached to Confluence. Rejected directions
remain temporary and are removed after selection. If Confluence is unavailable,
leave attachment and synchronization status incomplete.

### Artifact iteration log

Do not overwrite an artifact that reviewers have already used. Add a new
iteration with a new filename and checksum and mark the prior artifact as
`Superseded`.

| Iteration | Date | Change | Artifacts | Status |
|---|---|---|---|---|
| `v1` | YYYY-MM-DD | Initial selected design | `<KEY>-ui-01-state.png` | Pending upload |

## Decisions and alternatives

| Decision | Choice and rationale | Alternatives considered | Consequences |
|---|---|---|---|
| D1 | Choice | Alternatives | Consequences |

## Impact assessment

### Frontend

Describe the impact or explain why there is no impact.

### API/backend

Describe the impact or explain why there is no impact.

### Pipeline

Describe the impact or explain why there is no impact.

### Data

Cover schemas, storage, indexing, migration, retention, lineage, and privacy, or
explain why there is no impact.

### Agent/AI

Cover prompts, models, tools, orchestration, evaluation, safety, latency, and
cost, or explain why there is no impact.

### Infrastructure and deployment

Describe the impact or explain why there is no impact.

### Security and privacy

Describe the impact or explain why there is no impact.

### Operations and observability

Cover logging, metrics, tracing, alerts, support, and failure recovery, or
explain why there is no impact.

### Test strategy

Map unit, integration, contract, end-to-end, performance, security, and
acceptance verification to the affected behavior.

### Rollout and rollback

Describe sequencing, feature flags, compatibility, migration, monitoring,
rollback triggers, and recovery.

## Dependencies and implementation sequence

1. Dependency or implementation step.

## Acceptance-criteria traceability

| AC | Components | Implementation tasks | Verification |
|---|---|---|---|
| AC1 | Components | Tasks | Tests/checks |

## Revision log

| Date | Story/design change | Invalidated decisions | Status | Approved by |
|---|---|---|---|---|
| YYYY-MM-DD | Initial design | None | Proposed | Not approved |

## Publication checklist

- [ ] Requester approved the current story revision/hash.
- [ ] Canonical Markdown and `INDEX.md` are updated.
- [ ] Confluence page was created or updated successfully.
- [ ] Required UI mockups are attached to the Confluence page and recorded in
      the UI design artifact inventory.
- [ ] Confluence URL is recorded in Document control.
- [ ] Jira story links to the Confluence page.
- [ ] Git and Confluence content are synchronized.
