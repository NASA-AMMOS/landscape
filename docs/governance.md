# Governance

## Stewardship

The Open Mission Software Landscape is hosted under **NASA-AMMOS** and
maintained by `@NASA-AMMOS/landscape-maintainers` — a single core team
that reviews and merges every change.

Maintainership is open. Active and trusted contributors — from any NASA
center, partner organization, university, commercial space company, or
community project — can be nominated to the core maintainer team. The
current maintainers vote on additions.

## Scope

Open-source software, mission-related, with a public code repository.
That's it. See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the full
inclusion checklist.

**In scope:** NASA-developed OSS, partner-developed OSS (other agencies,
universities, commercial, foundations, individuals) — equally welcome.

**Out of scope:**

- Closed-source software.
- Government-source-only releases.
- ITAR / EAR-controlled software.
- Software that is not mission-related.
- Software without a public repository.

If a project has both an open-source and a closed-source flavor, the
landscape lists the **open-source** repo and may note the closed parent
in the description if relevant.

## Review process

Every change goes through PR review. There is no other way to mutate
the catalog.

1. **Author opens a PR** editing `landscape.yml` (or the relevant
   supporting file).
2. **CI runs `landscape2 validate`.** Schema errors block merge.
3. **CODEOWNERS auto-requests review** from `@NASA-AMMOS/landscape-maintainers`.
4. **At least one maintainer approval is required** to merge content
   PRs. Two approvals required for governance changes (CODEOWNERS,
   scope, taxonomy restructure).
5. **Squash-merge to `main`** triggers the build-and-deploy workflow,
   which publishes to GitHub Pages.

Maintainer review focuses on:

- License — confirmed open-source per `CONTRIBUTING.md`?
- Scope — genuinely mission-related?
- Annotations — `submitter.org` and `submitter.type` set; `nasa.center`
  set for NASA items?
- Description — accurate and current?
- Subcategory — placed correctly per `docs/category-taxonomy.md`?

## Partner submissions

Partner organizations submit through the same PR flow as NASA items.
The same inclusion criteria apply. The `submitter.*` annotation captures
who maintains the item; partners are not required to populate any
`nasa.*` annotations unless their software has explicit NASA mission
heritage worth surfacing.

## Standing up the team

Before going live, the NASA-AMMOS org admin needs to create the team
`@NASA-AMMOS/landscape-maintainers`, populate it with appropriate
maintainers, and grant write access to this repository. Teams can be
created at: `https://github.com/orgs/NASA-AMMOS/new-team`.

## Disputes

If maintainers disagree on inclusion or categorization, the team's
internal vote settles it. Escalation path: file an issue tagged
`governance` and include all parties.

## Removal vs. archival

Prefer **archival** (`project: archived`) over deletion. Archived items
render greyed-out in the UI and preserve historical context. Reserve
hard removal for entries added in error.

## Refresh cadence

- **Build:** every push to `main`, plus nightly cron (refreshes
  GitHub-derived enrichment without a code change).
- **Catalog audit:** at least annually, the maintainers walk every
  category to mark stale entries archived.

## Initial seeding from `code.json`

The initial catalog was seeded in part using
[`tools/transform_code_json.py`](../tools/transform_code_json.py),
which proposes mission-related open-source projects from
`nasa/Open-Source-Catalog`. This was a **one-shot** seeding step, not
an ongoing mirror — every entry in `landscape.yml` was reviewed by a
maintainer before merge.
