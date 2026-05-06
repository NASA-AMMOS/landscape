# Implementation Guide — Open Mission Software Landscape

A phase-by-phase playbook for standing up the landscape repo using
Claude Code. Designed to be pasted into a Claude Code session as the
top-level task and worked through sequentially.

Each phase has a **Goal**, **Pre-conditions**, **Steps** (annotated as
either `[Claude Code]` or `[You]`), and a **Verify** check that
confirms the phase succeeded before moving to the next.

---

## What you will have at the end

- A public repo at `github.com/NASA-AMMOS/landscape`
- A live landscape at `https://nasa-ammos.github.io/landscape`
- 18 mission-related OSS items seeded across 7 categories
- CI that validates every PR
- A pipeline for bulk-importing more items from `code.json`

Estimated wall-clock time: **45–90 minutes**, gated mostly on org-admin
steps you cannot delegate (team creation, secrets).

---

## Inputs you should have ready

1. The repo tarball generated previously: `landscape.tar.gz`
2. Owner-level access (or the ability to ask an owner) on the
   `NASA-AMMOS` GitHub organization
3. A GitHub Personal Access Token (PAT) with `public_repo` scope, for
   `LANDSCAPE_GH_TOKENS` (the build uses this for enrichment)
4. A working `gh` CLI: `gh --version` should print a version string
5. Docker (or Podman aliased as docker), used by the local validate script

---

## Phase 0 — Org-admin prerequisites

**Goal:** Create the GitHub-side artifacts only an org owner can create.

The repo `NASA-AMMOS/landscape` already exists as **private**. Two
decisions and two artifacts are still needed.

### Decide

**[You]** Pick a visibility plan for launch:

- **Path A — make public before Phase 4 (recommended).** GitHub Pages
  on a public repo is free and works with the shipped workflow as-is.
  Switch the repo to public in Phase 3 step 0.
- **Path B — keep private.** Pages from a private repo requires GitHub
  Enterprise Cloud (NASA-AMMOS likely has this). The site itself can
  then be either org-internal or public-on-the-web. No code changes
  needed; you'll set this in Phase 3 step 2.

The rest of the guide assumes Path A. If you take Path B, watch for
the `[Path B]` callouts.

### Steps

1. **[You]** Create the GitHub team that gates reviews:
   - Browse to `https://github.com/orgs/NASA-AMMOS/new-team`
   - Name: `landscape-maintainers`
   - Description: "Reviewers for the Open Mission Software Landscape"
   - Visibility: Visible
   - Privacy: Closed
   - Add at least 2 initial members (yourself + one backup)

2. **[You]** Generate the build PAT:
   - `https://github.com/settings/tokens/new`
   - Note: "NASA-AMMOS landscape — build enrichment"
   - Scopes: `public_repo` only (nothing else — the build needs this
     to fetch metadata from listed projects' public repos, not from
     this repo itself)
   - Expiration: 1 year (set a calendar reminder)
   - Copy the token. You will paste it into a repo secret in Phase 3.

### Verify

```bash
gh team list NASA-AMMOS | grep landscape-maintainers
gh repo view NASA-AMMOS/landscape
```
Both succeed.

---

## Phase 1 — Local bootstrap

**Goal:** Unpack the tarball, initialize git, push to the empty repo.

### Steps

1. **[Claude Code]** Verify Claude Code session is in an empty parent
   directory and the tarball is accessible:
   ```bash
   ls -la landscape.tar.gz
   ```

2. **[Claude Code]** Extract and enter the directory:
   ```bash
   tar -xzf landscape.tar.gz
   cd landscape
   ls
   ```
   Expected at root: `landscape.yml`, `settings.yml`, `guide.yml`,
   `CODEOWNERS`, `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `LICENSE`,
   `IMPLEMENTATION_GUIDE.md`, `.gitignore`, plus `.github/`, `docs/`,
   `logos/`, `tools/`.

3. **[Claude Code]** Replace the LICENSE placeholder with the real
   Apache 2.0 text:
   ```bash
   curl -fsSL https://www.apache.org/licenses/LICENSE-2.0.txt -o LICENSE
   { echo "Copyright 2026 California Institute of Technology / NASA-AMMOS"; \
     echo ""; cat LICENSE; } > LICENSE.tmp && mv LICENSE.tmp LICENSE
   ```

4. **[Claude Code]** Run a sanity check on the data file before committing:
   ```bash
   pip install -r tools/requirements.txt
   python3 -c "
   import yaml
   doc = yaml.safe_load(open('landscape.yml'))
   for cat in doc['categories']:
       for sub in cat['subcategories']:
           for item in sub.get('items', []):
               assert item.get('logo'), f'{item[\"name\"]}: missing logo'
               ann = (item.get('extra') or {}).get('annotations') or {}
               assert 'submitter.org' in ann, f'{item[\"name\"]}: missing submitter.org'
               assert 'submitter.type' in ann, f'{item[\"name\"]}: missing submitter.type'
   print('OK')
   "
   ```

5. **[Claude Code]** Initialize git and push:
   ```bash
   git init -b main
   git add .
   git commit -m "Initial seed: 18 OSS items across 7 categories"
   git remote add origin https://github.com/NASA-AMMOS/landscape.git
   git push -u origin main
   ```

### Verify

`gh repo view NASA-AMMOS/landscape --web` opens
the repo with files visible. The README renders.

---

## Phase 2 — Local toolchain & first build

**Goal:** Confirm landscape2 builds cleanly on your machine before
relying on CI.

### Steps

1. **[Claude Code]** Install landscape2 CLI. Pick one:
   ```bash
   # macOS
   brew install cncf/landscape2/landscape2

   # Linux/macOS via shell installer
   curl --proto '=https' --tlsv1.2 -LsSf \
     https://github.com/cncf/landscape2/releases/download/v1.1.0/landscape2-installer.sh | sh

   # Or use the container image (no install)
   alias landscape2='docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/cncf/landscape2:latest'
   ```
   Verify: `landscape2 --help` returns the usage block.

2. **[Claude Code]** Validate all three input files:
   ```bash
   landscape2 validate data --data-file landscape.yml
   landscape2 validate settings --settings-file settings.yml
   landscape2 validate guide --guide-file guide.yml
   ```
   All three must print success. Schema errors surface with line numbers.

3. **[Claude Code]** Do a build without GitHub enrichment:
   ```bash
   landscape2 build \
     --data-file landscape.yml \
     --settings-file settings.yml \
     --guide-file guide.yml \
     --logos-path logos \
     --output-dir build
   ```
   You will see `WARN ... github tokens not provided` — expected for the
   local dry-run. The build should still complete.

4. **[Claude Code]** Serve and visually verify:
   ```bash
   landscape2 serve --landscape-dir build &
   echo "Visit http://127.0.0.1:8000 — verify the 7 categories render."
   ```

5. **[You]** Open the URL, confirm:
   - 7 categories render in their groupings
   - Items appear with the placeholder logo
   - Detail panels show repo_url, description, annotations
   - Guide tab shows category descriptions

6. **[Claude Code]** Stop the server: `kill %1` (or close the terminal).

### Verify

`build/index.html` exists, opens in a browser, and the landscape is
visually reasonable.

---

## Phase 3 — GitHub configuration

**Goal:** Wire up secrets, branch protection, and Pages.

### Steps

0. **[You]** Set repo visibility per your Phase 0 decision:
   - **Path A (public):** flip the repo to public:
     ```bash
     gh repo edit NASA-AMMOS/landscape --visibility public --accept-visibility-change-consequences
     ```
   - **Path B (private + GHE Pages):** confirm the org is on GitHub
     Enterprise Cloud and Pages is enabled for private repos:
     `gh api /orgs/NASA-AMMOS | grep plan` should show an Enterprise
     plan. If not, escalate before continuing.

1. **[Claude Code]** Set the build PAT as a repo secret:
   ```bash
   gh secret set LANDSCAPE_GH_TOKENS \
     --repo NASA-AMMOS/landscape
   # paste the PAT from Phase 0 step 3 when prompted
   ```

2. **[Claude Code]** Enable GitHub Pages with Actions as the source:
   ```bash
   gh api \
     --method POST \
     -H "Accept: application/vnd.github+json" \
     /repos/NASA-AMMOS/landscape/pages \
     -f build_type=workflow
   ```
   If this returns 409 (already exists), Pages is already enabled — fine.

3. **[Claude Code]** Apply branch protection on `main`:
   ```bash
   gh api \
     --method PUT \
     -H "Accept: application/vnd.github+json" \
     /repos/NASA-AMMOS/landscape/branches/main/protection \
     -f "required_status_checks[strict]=true" \
     -f "required_status_checks[contexts][]=Schema + logo checks" \
     -F enforce_admins=false \
     -f "required_pull_request_reviews[required_approving_review_count]=1" \
     -f "required_pull_request_reviews[require_code_owner_reviews]=true" \
     -f "restrictions=null"
   ```

4. **[You]** Confirm the team has write access:
   - `https://github.com/NASA-AMMOS/landscape/settings/access`
   - Add team `landscape-maintainers` with **Write** role

### Verify

```bash
gh secret list --repo NASA-AMMOS/landscape
gh api /repos/NASA-AMMOS/landscape/pages
gh api /repos/NASA-AMMOS/landscape/branches/main/protection
```
All three return populated responses, no 404s.

---

## Phase 4 — First deploy

**Goal:** Trigger the build-and-deploy workflow and verify the live site.

### Steps

1. **[Claude Code]** Trigger the workflow manually:
   ```bash
   gh workflow run build-and-deploy.yml \
     --repo NASA-AMMOS/landscape
   ```

2. **[Claude Code]** Watch it run:
   ```bash
   sleep 5
   gh run list --workflow=build-and-deploy.yml \
     --repo NASA-AMMOS/landscape --limit 1
   gh run watch --repo NASA-AMMOS/landscape
   ```
   Build job runs in `ghcr.io/cncf/landscape2`. ~3–5 minutes for the
   first run (no cache yet).

3. **[Claude Code]** Once green, the deploy step prints the live URL:
   ```bash
   gh run view --log --repo NASA-AMMOS/landscape | grep page_url
   ```

4. **[You]** Open the live URL. Same visual checks as Phase 2 step 5,
   plus this time GitHub-derived data should populate (stars, contributors,
   last-commit) on item cards.

### Verify

The site is reachable at
`https://nasa-ammos.github.io/landscape/` and item
cards show non-zero star counts where applicable.

---

## Phase 5 — Initial bulk seed from code.json

**Goal:** Use the transformer to surface candidate items from
`nasa/Open-Source-Catalog`, triage, merge approved entries.

### Steps

1. **[Claude Code]** On a fresh branch, run the transformer:
   ```bash
   git checkout -b seed/code-json-batch-1
   python3 tools/transform_code_json.py \
     --source https://raw.githubusercontent.com/nasa/Open-Source-Catalog/master/code.json \
     --output tools/_proposed/
   ```

2. **[Claude Code]** Triage one category at a time:
   ```bash
   ls tools/_proposed/
   ```
   For each `.proposed.yml`, walk through items. For each candidate ask:
   - Is the description still accurate (some catalog entries are stale)?
   - Is the repo still maintained? (`gh repo view <url>`)
   - Is the subcategory placement right?
   - Is `submitter.org` correct, or did the transformer guess wrong?

   Reject by deleting from the proposal file. Approve by copying into
   `landscape.yml` under the correct subcategory, alphabetical order.

3. **[Claude Code]** Validate locally:
   ```bash
   ./tools/validate_local.sh
   ```

4. **[Claude Code]** Clean up and commit:
   ```bash
   rm -rf tools/_proposed/
   git add landscape.yml
   git commit -m "Seed batch 1: bulk import from nasa/Open-Source-Catalog"
   git push -u origin seed/code-json-batch-1
   gh pr create --fill --base main --head seed/code-json-batch-1
   ```

5. **[You]** Have a second maintainer review for batches >5 items. Merge
   when CI is green.

### Verify

After merge, the next build (`gh workflow run build-and-deploy.yml`)
shows the new items live.

---

## Phase 6 — Logo backlog

**Goal:** Track the logo gap so the placeholder does not become permanent.

### Steps

1. **[Claude Code]** File a tracking issue listing every placeholder item:
   ```bash
   python3 - <<PY
   import yaml
   doc = yaml.safe_load(open("landscape.yml"))
   pending = []
   for c in doc["categories"]:
       for s in c["subcategories"]:
           for i in s.get("items", []):
               if i.get("logo") == "placeholder.svg":
                   pending.append(f"- [ ] **{i[\"name\"]}** ({c[\"name\"]} / {s[\"name\"]}) — repo: {i.get(\"repo_url\",\"n/a\")}")
   body = "Items still using `placeholder.svg`. Replace with a real SVG when available.\n\n" + "\n".join(pending)
   open("/tmp/logo-issue.md", "w").write(body)
   PY
   gh issue create \
     --repo NASA-AMMOS/landscape \
     --title "Logo backlog: items using placeholder.svg" \
     --label "logo-needed" \
     --body-file /tmp/logo-issue.md
   ```

2. As real SVGs come in, drop them in `logos/`, update the `logo:` field
   on the relevant item, check the box in the tracking issue.

### Verify

The issue exists, lists every placeholder-using item, labeled `logo-needed`.

---

## Phase 7 — Onboarding the maintainer team

**Goal:** Other maintainers can review and merge without depending on you.

### Steps

1. **[You]** In the team page (`https://github.com/orgs/NASA-AMMOS/teams/landscape-maintainers`):
   - Add a description of what the team does
   - Pin the repo
   - Add other maintainers (centers, partners) as members

2. **[You]** Walk new maintainers through:
   - The README local-build instructions
   - `docs/governance.md` (review process)
   - `docs/annotation-schema.md` (the required `submitter.*` fields)
   - The `CLAUDE.md` (repo conventions for Claude Code users)

3. **[Claude Code]** Optionally, add a `CONTRIBUTORS.md` acknowledging
   initial maintainers — small but meaningful for partner orgs.

### Verify

A second maintainer (not you) successfully reviews and approves a test PR.

---

## Common failure modes

**Pages 404 after first deploy.** SPA routing — confirm
`build-and-deploy.yml` has the `cp build/index.html build/404.html` step.
(It does in the shipped version.)

**`landscape2 validate` complains about `color1`.** Settings.yml brand
colors must be RGBA strings: `"rgba(11, 61, 145, 1)"`. Hex will not work.

**CODEOWNERS is not enforcing review.** Branch protection must have
`require_code_owner_reviews: true`. Phase 3 step 3 sets this; if skipped,
re-run that command.

**Build job times out fetching GitHub data.** Add more PATs to
`LANDSCAPE_GH_TOKENS` — comma-separated, parallelizes by token count.

**Transformer imports a stale or unmaintained project.** That is the
human-triage step job to catch. Do not merge a proposal you have not
spot-checked.

**A NASA-1.3 (NOSA) item shows the wrong license badge.** landscape2
reads license from GitHub by default. If detection is wrong, set
`license: NASA-1.3` explicitly on the item; the override takes precedence.

---

## Where to go after launch

- **Quarterly:** run the transformer against the latest `code.json` to
  catch newly-released NASA OSS. Triage and merge a batch.
- **Annually:** maintainer team walks every category, marks stale items
  `project: archived`.
- **As partners join:** demo the submission flow at SpaceOps or similar.
  The `submitter.type` enum supports commercial, academic, agency,
  community, and consortium contributors.
- **Logo cleanup:** chip away at the `logo-needed` backlog. Real SVGs
  meaningfully improve the visual coherence of the landscape.

---

## Appendix — useful one-liners

```bash
# Count items by submitter type
python3 -c "
import yaml, collections
c = collections.Counter()
for cat in yaml.safe_load(open('landscape.yml'))['categories']:
    for s in cat['subcategories']:
        for i in s.get('items', []):
            c[(i.get('extra') or {}).get('annotations',{}).get('submitter.type','?')] += 1
for k, v in c.most_common(): print(f'{v:4d}  {k}')
"

# Find items missing a real logo
grep -B1 'placeholder.svg' landscape.yml | grep '^      - name:'

# Force a fresh build (bypass cache)
gh workflow run build-and-deploy.yml \
  --repo NASA-AMMOS/landscape

# Tail a running workflow
gh run watch --repo NASA-AMMOS/landscape

# List recent runs
gh run list --workflow=build-and-deploy.yml \
  --repo NASA-AMMOS/landscape --limit 10
```
