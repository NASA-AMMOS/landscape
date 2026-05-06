# Open Mission Software Landscape

An interactive landscape of **open-source software** developed by NASA and
its partners for use in **space mission design, ground systems, mission
operations, and science data processing**. Generated with
[CNCF landscape2](https://github.com/cncf/landscape2).

> **Scope:** Open-source only. NASA-developed and external-partner
> (other agencies, universities, commercial, and independent developers)
> contributions are equally welcome. Closed, government-source-only,
> ITAR/EAR-controlled, or SRA-licensed software is out of scope.
> See [`docs/governance.md`](docs/governance.md).

## Repository layout

```
.
├── landscape.yml            # Canonical data file — all items live here
├── settings.yml             # landscape2 settings (facets, groups, colors)
├── guide.yml                # Per-category guide content
├── logos/
│   └── placeholder.svg      # Temporary logo for items without a real SVG
├── tools/
│   ├── transform_code_json.py # ONE-SHOT seed importer (not a recurring sync)
│   └── validate_local.sh    # Run validate locally with the landscape2 image
├── docs/
│   ├── annotation-schema.md # nasa.* / partner.* annotation conventions
│   ├── category-taxonomy.md # What goes where
│   └── governance.md        # Maintainer team, review process, scope
├── .github/workflows/       # validate (PR) + build-and-deploy (main + nightly)
└── CODEOWNERS               # Single landscape-maintainers team
```

## Local development

```bash
# Install landscape2
brew install cncf/landscape2/landscape2     # or use the container image

# Build
landscape2 build \
  --data-file landscape.yml \
  --settings-file settings.yml \
  --guide-file guide.yml \
  --logos-path logos \
  --output-dir build

# Serve
landscape2 serve --landscape-dir build
```

For full GitHub data enrichment (stars, contributors, languages, last-release
date), export `GITHUB_TOKENS` with one or more PATs scoped to `public_repo`.

## Contributing

Open a PR that edits `landscape.yml` — adding items in the appropriate
subcategory, alphabetical by name. NASA staff and external partners use
the same flow; see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Governance

Maintained by the `@NASA-AMMOS/landscape-maintainers` team — a small group
of core reviewers with subject-matter coverage across the catalog. See
[`docs/governance.md`](docs/governance.md).

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
