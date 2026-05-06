# Contributing

Thanks for helping grow the Open Mission Software Landscape. NASA staff,
partner-agency staff, university researchers, commercial vendors, and
independent developers are all welcome to propose additions.

## Inclusion criteria

An item is in scope if **all** of the following are true:

1. **It is open source.** The primary repository must carry an OSI-approved
   license (Apache-2.0, MIT, BSD-2/3-Clause, GPL family, MPL-2.0, etc.) or
   the [NASA Open Source Agreement (NOSA / NASA-1.3)](https://opensource.org/license/nasa-1-3).
   Government-source-only and SRA-licensed software is not in scope.
2. **It is mission-related.** It serves spacecraft mission design, ground
   data systems, flight software, mission operations, science data
   processing, instrument operations, or directly supporting standards
   and tooling.
3. **It has a public code repository.** GitHub is preferred (so automated
   enrichment works). GitLab and self-hosted Git also acceptable but won't
   auto-enrich.
4. **It is reasonably maintained or has historical significance.** Archived
   projects can stay (mark with `project: archived`); abandoned one-off
   prototypes generally should not be added.

## How to propose a new item

1. Identify the right category and subcategory in
   [`docs/category-taxonomy.md`](docs/category-taxonomy.md). If the item
   spans multiple, pick a primary and use `second_path` for the others.
2. Open a PR that edits **`landscape.yml`**, inserting your item
   alphabetically by `name` within the chosen subcategory.
3. At minimum, populate: `name`, `homepage_url`, `logo`, `description`,
   `repo_url`, `license`, and the appropriate annotations
   (see [`docs/annotation-schema.md`](docs/annotation-schema.md)):
    - For NASA-developed items, set `extra.annotations.nasa.center`
    - For partner-maintained items, set `extra.annotations.submitter.org`
      and `extra.annotations.submitter.type`
4. **Logo.** If you don't have a real SVG yet, use `placeholder.svg`.
   Real logos are preferred and a maintainer may ask for one before
   merging if a public mark exists. Items relying on `placeholder.svg`
   are tracked for follow-up; we expect to systematically replace them
   over time.
5. CI runs `landscape2 validate` automatically. Address any schema errors
   before review.
6. The `@NASA-AMMOS/landscape-maintainers` team is auto-requested for
   review. At least one approval is required to merge.

## Modifying or removing an item

Same flow — edit `landscape.yml`. To archive, set `project: archived`
rather than removing the entry, so historical context is preserved.

## A note for external partners

If you're contributing on behalf of a non-NASA organization, the only
extra step is using the `partner.*` annotation namespace instead of
(or alongside) `nasa.*`. There is no separate process, no separate
gatekeeper, and no preference given to NASA-origin items in review.

## Bulk seed imports

The initial seeding from `nasa/Open-Source-Catalog`'s `code.json` was a
one-time operation via `tools/transform_code_json.py`. The transformer
is retained for future ad-hoc seeding (e.g., importing from another
agency's catalog), but the landscape is not a continuous mirror of any
external source. See [`tools/README.md`](tools/README.md).
