#!/usr/bin/env python3
"""Verify that every item's `extra.tag` matches the union derived from its
NASA / submitter annotations. Run from repo root.

Expected tag set per item:
  - submitter-<submitter.type>
  - center-<nasa.center>                   (if present)
  - center-<x> for each x in nasa.contributing_centers
  - ammos-<nasa.ammos_element>             (if present)

All values are lowercased; whitespace and surrounding quotes are stripped.

Exits 0 on success, 1 on mismatch (printing every offending item).
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


def expected_tags(annotations: dict) -> list[str]:
    tags: list[str] = []
    if (st := annotations.get("submitter.type")):
        tags.append(f"submitter-{st.strip().lower()}")
    if (c := annotations.get("nasa.center")):
        tags.append(f"center-{c.strip().lower()}")
    if (cc := annotations.get("nasa.contributing_centers")):
        for x in str(cc).split(","):
            x = x.strip()
            if x:
                tags.append(f"center-{x.lower()}")
    if (ae := annotations.get("nasa.ammos_element")):
        tags.append(f"ammos-{ae.strip().lower()}")
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
            "submitter-<type>, center-<nasa.center>, center-<contributing>, "
            "ammos-<element>. Update the item's `tag:` block to match its "
            "annotations (or vice versa)."
        )
        return 1

    print(f"all {total} items: tag/annotation in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
