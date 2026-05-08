# Category Taxonomy

Seven top-level categories. All items live in `landscape.yml`,
organized under `categories: → subcategories: → items:`.

## Mission Design & Navigation

The "before launch" software family — design, analyze, and optimize
spacecraft trajectories and orbits. Includes mission analysis &
trajectory design, orbit determination, maneuver design and analysis,
ephemerides, gravity modeling, and multidisciplinary design
optimization (MDAO).

**Subcategories:** Mission Analysis & Trajectory Design.

## Mission Planning, Sequencing & Analysis

Tooling that turns goals into commands. Activity planning, sequence
generation/validation, downlink analysis, resource scheduling, relay
planning, and the open specs that bridge them.

**Subcategories:** Activity Planning & Scheduling; Sequence
Generation & Specifications.

## Instrument Data System

The science-side of operations: instrument commanding, calibration,
science product management, visualization, and image
processing/mapping.

**Subcategories:** Science Data Visualization & Mapping; Instrument
Toolkits & GDS; Mission Control Integration.

## Mission Control System

Flying the spacecraft: telemetry & command, secure uplink/downlink,
data management, ops visualization, monitoring, testbed support.

**Subcategories:** Operations Visualization.

## Ground Software Foundations

Frameworks and substrates that mission software is **built on**. Use
this for general-purpose engines that aren't tied to a single mission
phase.

**Subcategories:** Flight Software Frameworks; Simulation & Test.

## Earth & Science Data Systems

Cloud-native pipelines, services, and visualization for Earth and
space science archives. ESDIS-class infrastructure rather than
mission-specific operations software.

**Subcategories:** Data Access & APIs; Processing Pipelines &
Algorithms; Imagery & Visualization Services.

## Developer Tools & Standards

Cross-cutting tooling for *how* mission software is built.
Best-practices automation, lifecycle modernization, open specs.

**Subcategories:** Best Practices & Lifecycle.

---

## When an item fits multiple categories

Use `second_path` rather than duplicating the item:

```yaml
second_path:
  - "Instrument Data System / Mission Control Integration"
  - "Mission Control System / Operations Visualization"
```

Pick the most natural primary; alternates surface in those other
buckets without a second card.

## Adding a new subcategory

Subcategories are listed both in `landscape.yml` (under the
appropriate category) and in `settings.yml` (which controls
ordering). Update both.

## Adding a new top-level category

1. Add the category to `landscape.yml` with at least one subcategory.
2. Add the category to `settings.yml` under `categories:` and at
   least one `groups:` entry.
3. Add a `categories:` entry in `guide.yml` describing it.
4. Open a PR. Category additions require two stewards approvals.
