# StoryOS Artifact Specification

**Project:** StoryOS
**Module:** `storyos.artifacts`
**Milestone:** M0 — Typed Contracts
**Status:** Frozen
**Version:** 1.1

---

# Purpose

The `artifacts` module defines every data contract exchanged between agents.

Agents never communicate through free-form text or provider-specific objects. Every stage receives one or more typed artifacts and produces another typed artifact.

This architecture provides:

- Strong validation
- Replaceable agents
- Independent testing
- Complete traceability
- Deterministic orchestration
- Future persistence support

---

# Architecture

```
                     Topic
                       │
                       ▼
                  Planner Agent
                       │
                     Plan
                       │
                       ▼
                Research Agent
                       │
                    Dossier
                       │
                       ▼
                  Angle Agent
                       │
                     Angle
                       │
                       ▼
                 Outline Agent
                  (Dossier + Angle)
                       │
                    Outline
                       │
                       ▼
                  Draft Agent
          (Dossier + Angle + Outline + ChannelDNA)
                       │
                     Draft
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    Critic        Fact Check      Voice        [Specialists]
        │              │              │              │
        ▼              ▼              ▼              ▼
 CriticReport  FactCheckReport  VoiceReport   SpecialistReport(s)
        └──────────────┴──────────────┴──────────────┘
                       ▼
               FeedbackBundle
              (Orchestrator merges,
          verifies shared draft_ref)
                       │
                       ▼
                  Draft Agent
                  (Revision)
                       │
                       ▼
                 Visual Agent
                       │
                VisualBeatSheet
                       │
                       ▼
            Final Production Package
```

**v1.1 change from v1.0:** `Draft Agent` now consumes `Angle` directly, not only `Outline`. Rationale below, under **Rule 10**.

---

# Directory Structure

```
artifacts/
├── __init__.py
├── base.py
├── common.py
├── dossier.py
├── angle.py
├── outline.py
├── draft.py
├── critic.py
├── fact_check.py
├── feedback.py
├── voice.py
├── visual.py
├── channel_dna.py
└── plan.py
```

---

# Base Layer

## BaseArtifact

Parent class for every artifact.

### Responsibilities

- Shared metadata
- Schema validation
- Traceability

### Fields

| Field | Purpose |
|--------|----------|
| id | Unique artifact identifier |
| artifact_type | Logical artifact type |
| run_id | Pipeline execution ID |
| producer | Producing agent |
| schema_version | Schema version (contract version — distinct from `Draft.iteration`, which tracks revision count) |
| created_at | Creation timestamp |

---

## common.py

Shared reusable value objects.

Currently contains:

```
Severity
```

Add future reusable types here only once a second entity needs the same shape — not preemptively.

---

# Research Layer

## Fact

Represents one atomic factual statement.

### Produced by

Research Agent

### Fields

| Field |
|--------|
| id |
| statement |
| source |
| confidence |

---

## Dossier

Single source of truth for the pipeline.

Only this artifact may introduce facts.

### Produced by

Research Agent

### Consumed by

- Angle
- Outline
- Draft
- Fact Check

### Fields

| Field |
|--------|
| topic |
| executive_summary |
| facts |
| misconceptions |
| interesting_insights |
| analogies |

---

# Story Layer

## Angle

Defines the narrative direction.

### Produced by

Angle Agent

### Consumed by

- Outline Agent
- **Draft Agent** *(direct access — see Rule 10)*

### Fields

| Field |
|--------|
| title |
| core_premise |
| hook |
| why_this_angle |
| audience_takeaway |

---

## Beat

Single story beat.

### Fields

| Field |
|--------|
| id |
| order |
| title |
| objective |
| summary |
| fact_refs |

---

## Outline

High-level story structure.

### Produced by

Outline Agent

### Consumed by

Draft Agent

### Fields

| Field |
|--------|
| title |
| beats |

---

# Script Layer

## Draft

Complete script. Every revision creates a new immutable Draft.

### Produced by

Draft Agent

### Consumes

Dossier, **Angle**, Outline, ChannelDNA (+ FeedbackBundle on revision passes)

### Consumed by

- Critic
- Fact Check
- Voice
- Visual

### Fields

| Field |
|--------|
| title |
| script |
| beat_refs |
| iteration |

---

# Review Layer

## CriticNote

Single storytelling issue.

### Fields

| Field |
|--------|
| id |
| severity |
| beat_ref |
| line_ref |
| issue |
| recommendation |

---

## CriticReport

Narrative quality review.

### Produced by

Critic Agent

### Fields

| Field |
|--------|
| draft_ref |
| passed |
| overall_score |
| summary |
| notes |

---

## Flag

Single factual issue.

### Fields

| Field |
|--------|
| id |
| severity |
| line_ref |
| claim |
| reason |
| supporting_fact_refs |
| recommendation |

---

## FactCheckReport

Factual verification report.

### Produced by

Fact Check Agent

### Fields

| Field |
|--------|
| draft_ref |
| passed |
| summary |
| flags |

---

## DriftFlag

Single voice/style issue.

### Fields

| Field |
|--------|
| id |
| severity |
| beat_ref |
| line_ref |
| principle |
| observation |
| recommendation |

---

## VoiceReport

Voice consistency report.

### Produced by

Voice Agent

### Fields

| Field |
|--------|
| draft_ref |
| passed |
| overall_score |
| summary |
| flags |

---

# Revision Layer

## FeedbackSource

Enum

```
critic
fact_check
voice
specialist
```

---

## FeedbackItem

Normalized review issue.

### Fields

| Field |
|--------|
| id |
| source |
| source_ref |
| severity |
| beat_ref |
| line_ref |
| issue |
| recommendation |

---

## FeedbackBundle

Merged feedback for one revision iteration.

Produced only by the Orchestrator. Consumed only by the Draft Agent.

### Fields

| Field |
|--------|
| draft_ref |
| iteration |
| summary |
| total_findings |
| items |

---

# Production Layer

## VisualBeat

Production instructions for one beat.

### Fields

| Field |
|--------|
| id |
| beat_ref |
| line_refs |
| objective |
| visual_description |
| visual_type |
| assets |
| on_screen_text |
| transition |

---

## VisualBeatSheet

Complete editing plan.

### Produced by

Visual Agent

### Fields

| Field |
|--------|
| title |
| beats |

---

# Meta Layer

## ChannelDNA

Permanent creative identity. Read-only during execution. Updated only by the offline learning system.

### Consumed by

- Planner
- Research
- Angle
- Outline
- Draft
- Critic
- Voice

### Fields

| Field |
|--------|
| channel_name |
| mission |
| audience |
| value_proposition |
| storytelling_principles |
| humor_principles |
| writing_principles |
| banned_patterns |
| favorite_devices |
| intro_style |
| ending_style |
| pacing_style |
| default_recipe |

---

## Specialist

Optional review specialist.

### Fields

| Field |
|--------|
| name |
| enabled |
| objective |

---

## Plan

Execution plan generated by Planner. Read once by the Orchestrator.

### Fields

| Field |
|--------|
| outline_template |
| critic_rubric |
| specialists |
| revision_budget |

---

# Traceability Model

```
Fact
 │
 ▼
Dossier ──────────────┐
 │                     │
 ▼                     ▼
Outline Beat        Draft (also reads Angle directly)
 │                     │
 ▼                     ▼
                  CriticNote / Flag / DriftFlag
                     │
                     ▼
                 FeedbackItem
                     │
                     ▼
                 FeedbackBundle
                     │
                     ▼
                 Draft Revision
```

Every artifact references previous artifacts by ID. No artifact embeds another artifact directly.

---

# Ownership Matrix

| Artifact | Produced By | Consumed By |
|------------|-------------|-------------|
| Plan | Planner | Orchestrator |
| Dossier | Research | Angle, Outline, Draft, Fact Check |
| Angle | Angle | Outline, **Draft** |
| Outline | Outline | Draft |
| Draft | Draft | Critic, Fact Check, Voice, Visual |
| CriticReport | Critic | Orchestrator |
| FactCheckReport | Fact Check | Orchestrator |
| VoiceReport | Voice | Orchestrator |
| FeedbackBundle | Orchestrator | Draft |
| VisualBeatSheet | Visual | Final Output |
| ChannelDNA | Learning System | All Creative Agents |

---

# Architectural Rules

**Rule 1** — Only the Research Agent may introduce new factual information.

**Rule 2** — Every factual statement must originate from the Dossier.

**Rule 3** — Artifacts are immutable. Every revision creates a new artifact.

**Rule 4** — Artifacts reference each other using IDs instead of object references.

**Rule 5** — Every review report references the exact Draft it evaluated using `draft_ref`.

**Rule 6** — The Draft Agent's *revision* input is only `FeedbackBundle`. It never reads `CriticReport`, `FactCheckReport`, or `VoiceReport` directly.

**Rule 7** — The Orchestrator verifies that all review reports reference the same `draft_ref` before creating a `FeedbackBundle`.

**Rule 8** — `revision_budget` represents the total number of Draft revision iterations allowed across the entire review cycle, not per review agent.

**Rule 9** — ChannelDNA is read-only during execution. Only the offline learning system may update it.

**Rule 10 (new in v1.1)** — The Draft Agent consumes `Angle` directly, in addition to `Outline`. The Outline Agent's job is structure (beat order, objectives, fact references), not preserving exact hook phrasing or audience framing — those are Angle's specific content. Routing Draft's voice-critical input entirely through Outline creates a single point of failure: if the Outline Agent's beat summaries flatten the Angle's sharpest language during structural compression, that language never reaches the script. Giving Draft direct access to `Angle` costs nothing (it's a small artifact) and removes this dependency — Outline still owns structure, but Draft is no longer betting on perfect fidelity of translation for voice-critical content it wasn't designed to protect.

---

# Current Status

| Layer | Status |
|--------|--------|
| Base | ✅ Complete |
| Research | ✅ Complete |
| Story | ✅ Complete |
| Draft | ✅ Complete |
| Review | ✅ Complete |
| Revision | ✅ Complete |
| Production | ✅ Complete |
| Meta | ✅ Complete |

---

# M0 Completion Criteria

- ✅ Typed Pydantic contracts
- ✅ Strict validation
- ✅ Immutable artifacts
- ✅ Traceability by IDs
- ✅ Artifact ownership defined
- ✅ Producer/consumer relationships documented
- ✅ Public exports through `artifacts.__init__.py`
- ✅ Unit-testable independent models
- ✅ No circular dependencies
- ✅ Draft Agent's inputs finalized (Dossier + Angle + Outline + ChannelDNA)
- ✅ Stable contracts ready for agent implementation

---

# Known Deferred Item (not blocking M0)

`ChannelDNA.default_recipe` and `Plan` likely share structural overlap (both describe an outline template + critic rubric + specialists selection). Not deduplicated in this version — nothing else depends on them staying separate, so this can be extracted into a shared `RecipeDefaults` value object in `common.py` later without breaking existing contracts, once/if the duplication becomes a real maintenance cost.
