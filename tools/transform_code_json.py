#!/usr/bin/env python3
"""
transform_code_json.py — One-shot importer that proposes additions from
`nasa/Open-Source-Catalog`'s `code.json` for human review.

This is NOT a continuous mirror. It was used during initial seeding and
is retained for ad-hoc bulk-import work (e.g., importing from another
agency's catalog with a similar shape). After running it, a maintainer
copy/pastes approved entries into `landscape.yml` via PR — never
auto-merged.

Output: a single `seed-proposals.yml` file containing all candidates
grouped by best-guess category. Subcategory placement and fine-tuning
of descriptions/annotations are the maintainer's job.

Filtering rules (intentionally conservative):

  * License must be OSI-approved or NOSA. Government-source-only entries
    are dropped.
  * Public Code Repo must be set and resolve to a GitHub URL.
  * Description and/or categories must match mission-related keywords.
  * Items already present in `landscape.yml` (matched by repo URL) are
    skipped.

Usage:
  python3 tools/transform_code_json.py
  python3 tools/transform_code_json.py --source ./code.json
  python3 tools/transform_code_json.py --source <url> --output proposals.yml
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LANDSCAPE_FILE = REPO_ROOT / "landscape.yml"

MISSION_KEYWORDS = {
    "spacecraft", "satellite", "cubesat", "smallsat",
    "mission", "telemetry", "command", "sequencing", "sequence",
    "navigation", "orbit", "trajectory", "ephemeris", "ephemerides",
    "instrument", "payload", "downlink", "uplink",
    "ground system", "ground data", "gds", "egse",
    "flight software", "flight system",
    "spice", "ccsds", "xtce", "sle",
    "science data", "calibration", "data processing", "image processing",
    "remote sensing", "earth observation", "planetary",
    "operations", "mission control", "flight dynamics",
    "rover", "lander", "deep space",
    "autonomy", "autonomous",
}

MISSION_CATEGORY_TOKENS = {
    "Aeronautics", "Autonomous Systems", "Spacecraft",
    "Mission Operations", "Image Processing", "Data Processing",
    "Operations", "Communications", "Navigation",
    "Robotics", "Simulation", "Science Data",
    "Astrophysics", "Earth Science", "Planetary",
}

LICENSE_MAP = {
    "NASA Open Source": "NASA-1.3",
    "NASA Open Source Agreement": "NASA-1.3",
    "NOSA": "NASA-1.3",
    "Apache License, Version 2.0": "Apache-2.0",
    "Apache 2.0": "Apache-2.0",
    "Apache License 2.0": "Apache-2.0",
    "MIT License": "MIT",
    "BSD 3-Clause": "BSD-3-Clause",
    "BSD 2-Clause": "BSD-2-Clause",
    "GPL v2": "GPL-2.0",
    "GPL v3": "GPL-3.0",
    "MPL 2.0": "MPL-2.0",
    "Public Domain": "CC0-1.0",
}

ACCEPTABLE_LICENSES = {
    "Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause",
    "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0",
    "MPL-2.0", "ISC", "CC0-1.0", "NASA-1.3",
}

CENTER_NORMALIZE = {
    "Ames Research Center": "ARC", "ARC": "ARC",
    "Goddard Space Flight Center": "GSFC", "GSFC": "GSFC",
    "Jet Propulsion Laboratory": "JPL", "JPL": "JPL",
    "Johnson Space Center": "JSC", "JSC": "JSC",
    "Kennedy Space Center": "KSC", "KSC": "KSC",
    "Langley Research Center": "LaRC", "LARC": "LaRC", "LaRC": "LaRC",
    "Glenn Research Center": "GRC", "GRC": "GRC",
    "Marshall Space Flight Center": "MSFC", "MSFC": "MSFC",
    "Stennis Space Center": "SSC", "SSC": "SSC",
}

CATEGORY_ROUTES = [
    ("Mission Design & Navigation", {
        "trajectory", "orbit", "ephemeris", "navigation",
        "mission analysis", "mission design", "mdao",
    }),
    ("Mission Planning, Sequencing & Analysis", {
        "planning", "sequencing", "scheduling", "activity plan",
    }),
    ("Instrument Data System", {
        "instrument", "calibration", "image processing", "mapping",
        "science product", "vicar",
    }),
    ("Mission Control System", {
        "mission control", "telemetry", "command", "uplink", "downlink",
        "operations visualization",
    }),
    ("Ground Software Foundations", {
        "flight software", "simulation", "framework", "middleware",
        "trick", "cfs", "fprime", "f-prime", "f prime",
    }),
    ("Earth & Science Data Systems", {
        "earth science", "earth observation", "remote sensing",
        "data pipeline", "daac", "eosdis", "data archive",
    }),
    ("Developer Tools & Standards", {
        "best practices", "lifecycle", "specification", "standard",
        "developer tool",
    }),
]
DEFAULT_CATEGORY = "Ground Software Foundations"  # human-triage bucket

GITHUB_URL_RE = re.compile(r"https?://github\.com/[^/]+/[^/?#\s]+", re.IGNORECASE)


def load_source(source: str) -> Any:
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source) as resp:  # noqa: S310
            return json.load(resp)
    with open(source, "r", encoding="utf-8") as fh:
        return json.load(fh)


def existing_repo_urls() -> set[str]:
    if not LANDSCAPE_FILE.is_file():
        return set()
    with LANDSCAPE_FILE.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    existing: set[str] = set()
    for cat in doc.get("categories", []):
        for sub in cat.get("subcategories", []):
            for item in sub.get("items", []) or []:
                if url := item.get("repo_url"):
                    existing.add(url.rstrip("/").lower())
                for r in item.get("additional_repos", []) or []:
                    if url := r.get("repo_url"):
                        existing.add(url.rstrip("/").lower())
    return existing


def normalize_license(raw: Any) -> str | None:
    if not raw:
        return None
    candidates = raw if isinstance(raw, list) else [raw]
    for c in candidates:
        if not isinstance(c, str):
            continue
        if c in LICENSE_MAP:
            return LICENSE_MAP[c]
        if c in ACCEPTABLE_LICENSES:
            return c
    return None


def normalize_center(raw: Any) -> str | None:
    if not isinstance(raw, str):
        return None
    return CENTER_NORMALIZE.get(raw.strip(), raw.strip())


def is_mission_related(entry: dict) -> bool:
    haystack_parts: list[str] = []
    for key in ("Software", "Description"):
        v = entry.get(key, "")
        if isinstance(v, str):
            haystack_parts.append(v)
    cats = entry.get("Categories", []) or []
    if isinstance(cats, list):
        haystack_parts.extend(c for c in cats if isinstance(c, str))
        if any(c in MISSION_CATEGORY_TOKENS for c in cats):
            return True
    haystack = " ".join(haystack_parts).lower()
    return any(kw in haystack for kw in MISSION_KEYWORDS)


def extract_github_url(entry: dict) -> str | None:
    for key in ("Public Code Repo", "External Link"):
        val = entry.get(key, "")
        if isinstance(val, str):
            m = GITHUB_URL_RE.search(val)
            if m:
                return m.group(0).rstrip("/.,)")
    return None


def route_to_category(entry: dict) -> str:
    haystack = " ".join(
        str(entry.get(k, "")) for k in ("Software", "Description")
    ).lower()
    cats = " ".join(entry.get("Categories", []) or []).lower()
    haystack = f"{haystack} {cats}"
    for cat_name, keywords in CATEGORY_ROUTES:
        if any(kw in haystack for kw in keywords):
            return cat_name
    return DEFAULT_CATEGORY


def to_landscape_item(entry: dict) -> dict | None:
    name = entry.get("Software", "").strip()
    if not name:
        return None
    repo_url = extract_github_url(entry)
    if not repo_url:
        return None
    license_id = normalize_license(entry.get("License"))
    if license_id is None or license_id not in ACCEPTABLE_LICENSES:
        return None
    center = normalize_center(entry.get("NASA Center"))
    description = entry.get("Description", "").strip()
    if len(description) > 600:
        description = description[:597] + "..."

    return {
        "name": name,
        "homepage_url": entry.get("External Link") or repo_url,
        "logo": "placeholder.svg",
        "description": description or f"{name} (description pending).",
        "repo_url": repo_url,
        "license": license_id,
        "extra": {
            "annotations": {
                "nasa.center": center or "UNKNOWN",
                "distribution": "open-source",
            }
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="https://raw.githubusercontent.com/nasa/Open-Source-Catalog/master/code.json",
        help="URL or path to code.json",
    )
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "tools" / "seed-proposals.yml"),
        help="Output file for proposals",
    )
    args = parser.parse_args()

    print(f"Loading {args.source} ...")
    raw = load_source(args.source)

    if isinstance(raw, dict) and "projects" in raw:
        entries = raw["projects"]
    elif isinstance(raw, list):
        entries = raw
    else:
        raise SystemExit("❌ unrecognized source schema")

    print(f"  {len(entries)} entries in source")

    existing = existing_repo_urls()
    print(f"  {len(existing)} repo URLs already in landscape (will skip)")

    buckets: dict[str, list[dict]] = defaultdict(list)
    stats = {"considered": 0, "non_mission": 0, "no_repo": 0,
             "bad_license": 0, "duplicate": 0, "imported": 0}

    for entry in entries:
        stats["considered"] += 1
        if not is_mission_related(entry):
            stats["non_mission"] += 1
            continue
        item = to_landscape_item(entry)
        if item is None:
            if not extract_github_url(entry):
                stats["no_repo"] += 1
            elif normalize_license(entry.get("License")) not in ACCEPTABLE_LICENSES:
                stats["bad_license"] += 1
            continue
        if item["repo_url"].rstrip("/").lower() in existing:
            stats["duplicate"] += 1
            continue
        buckets[route_to_category(entry)].append(item)
        stats["imported"] += 1

    payload = {
        "_note": (
            "Proposed additions from a code.json source. Each item is a "
            "best-guess routing into a category — the maintainer chooses "
            "the correct subcategory and may need to refine the "
            "description, annotations, and license. Copy approved items "
            "into landscape.yml via PR. Items already present (matched by "
            "repo_url) are skipped."
        ),
        "proposals_by_category": [
            {"category": cat, "items": items}
            for cat, items in sorted(buckets.items())
        ],
    }
    out_path = Path(args.output)
    out_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    print(f"\n  → wrote {out_path}")

    print("\nSummary:")
    for k, v in stats.items():
        print(f"  {k:>14}: {v}")
    print(f"\n  Categories with proposals: {len(buckets)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
