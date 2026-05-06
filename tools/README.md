# tools/

Custom tooling that supplements the landscape2 CLI.

## `transform_code_json.py`

**One-shot** seed importer for `nasa/Open-Source-Catalog`'s `code.json`
(or any source with the same shape). The landscape is **not** a
continuous mirror of code.json — this tool runs ad-hoc when we want
to evaluate bulk additions.

```bash
python3 tools/transform_code_json.py
# → tools/seed-proposals.yml
```

Output is a single YAML file grouped by best-guess category. A
maintainer reviews each candidate, refines descriptions and
annotations as needed, and copies approved entries into
`landscape.yml` via PR. The transformer never touches `landscape.yml`
directly.

Filter rules (kept conservative on purpose):

- License must be OSI-approved or NOSA (NASA-1.3).
- Public code repo must be present and resolve to GitHub.
- Description / Categories must match mission-related keywords.
- Items already present (matched by `repo_url`) are skipped.

Use the same script with a different `--source` to bulk-evaluate other
agency / partner catalogs that publish similar JSON.

## `validate_local.sh`

Runs the same validation that CI runs, locally. Requires Docker.

```bash
./tools/validate_local.sh
```

## Dependencies

```bash
pip install -r tools/requirements.txt
```
