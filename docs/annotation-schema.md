# Annotation Schema

Landscape2 supports a free-form `extra.annotations` map on every item
(string keys, string values). We use it to capture metadata that the
upstream schema does not model — submitter attribution and NASA-specific
context.

## Conventions

- Annotations are namespaced. `submitter.*` for who maintains the item,
  `nasa.*` for NASA-specific attributes.
- Values are always strings. Lists are comma-separated.
- `submitter.org` and `submitter.type` are required for **every** item.
  `nasa.*` annotations are required only for NASA-maintained items.

## Required: submitter attribution (all items)

| Key | Required? | Allowed values | Notes |
|---|---|---|---|
| `submitter.org` | **Yes** | Free text | NASA center code (JPL, GSFC, ARC, ...) or partner org name (e.g. "Astrobotic Technology", "MIT Lincoln Lab", "ESA"). |
| `submitter.type` | **Yes** | `nasa-center` \| `commercial-partner` \| `academic` \| `agency-partner` \| `community` \| `consortium` | The kind of organization maintaining the item. |

For commercial partners with a Crunchbase entry, you can additionally
set the top-level `crunchbase` field (a landscape2 native) — landscape2
auto-pulls org info, logo, and funding data from there. NASA centers do
not have Crunchbase entries; rely on `submitter.org` for them.

## NASA-specific annotations (NASA-maintained items only)

| Key | Required? | Allowed values | Notes |
|---|---|---|---|
| `nasa.center` | **Yes for NASA items** | `JPL`, `GSFC`, `ARC`, `JSC`, `GRC`, `MSFC`, `LaRC`, `KSC`, `SSC`, `JHU-APL`, `HQ` | Primary maintaining center. Should match `submitter.org` for NASA items. |
| `nasa.contributing_centers` | No | Comma-separated center codes | When the project is genuinely cross-center. |
| `nasa.ammos_element` | No | `MDN`, `MPSA`, `IDS`, `MCS`, `SECURITY` | Set only for AMMOS-aligned products. |
| `nasa.distribution` | No | `open-source` (the only acceptable value here) | Sanity-check field; closed items should not be present in this landscape. |
| `nasa.sponsor_program` | No | e.g. `MGSS`, `ESDIS`, `AIST`, `SMD-funded`, `STMD` | Funding program / line of authority. |
| `nasa.missions` | No | Comma-separated list | Mission heritage — flown or scheduled. |
| `nasa.standards` | No | Comma-separated list | Open standards the project produces or consumes (CCSDS, XTCE, SLE, seq-json, etc.). |
| `nasa.trl` | No | `1`–`9` | Technology Readiness Level if claimed. |
| `nasa.cm_authority` | No | Free text | CCB or governance body, when one exists. |
| `nasa.slim_compliant` | No | `true` / `false` | SLIM best-practices adoption signal. |

Partner-maintained items **may** set selected `nasa.*` annotations if
the project has explicit NASA mission heritage worth surfacing — for
example, a commercial flight software framework that has flown on NASA
missions might set `nasa.missions` even though `nasa.center` is unset.
Use sparingly; the `nasa.*` namespace is meant primarily for
NASA-developed software.

## Avoid storing PII

Don't put named individuals' contact info in annotations. Use mailing-list
URLs, GitHub team handles, or org-level roles instead.

## Surfacing annotations as filters

Annotations pass through to the rendered landscape but are **not**
rendered as filterable facets by default. To make a value filterable,
also add it to the item's top-level `tag:` list. The `settings.yml`
`tags:` section enumerates which tag values appear as filter chips.

## Examples

### NASA-maintained item

```yaml
- name: Cumulus
  homepage_url: https://nasa.github.io/cumulus/
  logo: placeholder.svg
  description: >-
    Cloud-native framework for processing NASA Earth science data.
  repo_url: https://github.com/nasa/cumulus
  license: Apache-2.0
  extra:
    annotations:
      submitter.org: JPL
      submitter.type: nasa-center
      nasa.center: JPL
      nasa.distribution: open-source
      nasa.sponsor_program: ESDIS
```

### Partner-maintained item with NASA mission heritage

```yaml
- name: Example Commercial FSW
  homepage_url: https://example.com/fsw
  logo: placeholder.svg
  description: >-
    Commercial flight software framework with deployments on NASA
    smallsat missions.
  repo_url: https://github.com/example/fsw
  license: Apache-2.0
  crunchbase: https://www.crunchbase.com/organization/example-corp
  extra:
    annotations:
      submitter.org: Example Corp
      submitter.type: commercial-partner
      nasa.missions: "Hypothetical SmallSat-1"
```

### Academic / community item

```yaml
- name: Example University Tool
  homepage_url: https://example.edu/tool
  logo: placeholder.svg
  description: >-
    University-developed orbit determination toolkit.
  repo_url: https://github.com/example-edu/tool
  license: BSD-3-Clause
  extra:
    annotations:
      submitter.org: Example University
      submitter.type: academic
```
