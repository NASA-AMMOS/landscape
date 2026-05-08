#!/usr/bin/env python3
"""Verify that every item's `extra.tag` matches the union derived from its
NASA / submitter annotations. Run from repo root.

Tags are bare values (no namespace prefix) — landscape2's UI auto-prefixes
each chip with "TAG", so a tag of `center-jpl` would render as
"TAG CENTER JPL". Using bare values gives clean chips like "TAG JPL".

Expected tag set per item:
  - <x> for each x in nasa.contributing_centers
  - <nasa.ammos_element>       if present, e.g. mpsa

`nasa.center` is intentionally NOT mirrored as a tag — the
foundation+project badge ("NASA JPL", "NASA GSFC", ...) already
conveys the primary center, so a matching tag chip would render
the same fact twice on every card. Tags only carry information
the badge can't: cross-center collaboration (contributing centers)
and AMMOS element. `submitter.type` is also not mirrored (was
"nasa-center" for every item, redundant as a filter axis).

All values are lowercased; whitespace and surrounding quotes are stripped.

Exits 0 on success, 1 on mismatch (printing every offending item).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def expected_tags(annotations: dict) -> list[str]:
    tags: list[str] = []
    if (cc := annotations.get("nasa.contributing_centers")):
        for x in str(cc).split(","):
            x = x.strip()
            if x:
                tags.append(x.lower())
    if (ae := annotations.get("nasa.ammos_element")):
        tags.append(ae.strip().lower())
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def main() -> int:
    path = Path("landscape.yml")
    with path.open() as fh:
        doc = yaml.safe_load(fh)

    problems: list[str] = []
    total = 0
    for cat in doc["categories"]:
        for sub in cat.get("subcategories", []) or []:
            for item in sub.get("items", []) or []:
                total += 1
                extra = item.get("extra") or {}
                annotations = extra.get("annotations") or {}
                expected = expected_tags(annotations)
                actual = list(extra.get("tag") or [])
                if sorted(expected) != sorted(actual):
                    problems.append(
                        f"{item['name']}\n"
                        f"    expected: {expected}\n"
                        f"    actual:   {actual}"
                    )

    if problems:
        print("tag/annotation mismatch in landscape.yml:")
        for p in problems:
            print(f"  - {p}")
        print(
            "\nEvery item's `extra.tag` must equal the union of "
            "<each contributing center> and <nasa.ammos_element> — "
            "bare values, all lowercased. nasa.center is intentionally "
            "NOT mirrored as a tag (the project badge already shows it); "
            "submitter.type is also not mirrored. Update the item's "
            "`tag:` block to match its annotations (or vice versa)."
        )
        return 1

    print(f"all {total} items: tag/annotation in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
