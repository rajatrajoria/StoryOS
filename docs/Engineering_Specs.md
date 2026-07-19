# StoryOS — Product & Architecture Specification (v0.2)

**A multi-agent system that writes production-quality scripts for content creators, adaptable to genre, voice, and format.**

*This supersedes v0.1. Treat this as the project's constitution — the document every architectural decision gets checked against.*

---

## 1. Product Thesis

Generic AI script tools produce generic AI scripts — one prompt, one pass, competent but forgettable. The gap between that and what a real writers' room produces isn't model quality, it's *process*: research separated from structuring, structuring separated from drafting, and a deliberate critique-and-redraft loop before anything ships.

StoryOS's bet: encode that process as a pipeline of narrow, specialized agents instead of one generalist agent, and let the pipeline *adapt its own shape* per customer and per genre instead of forcing every script through identical steps.

**What "done well" looks like:** a customer runs a brief through StoryOS and gets a script that reads like it came from a writer who knows their channel — not a script that reads like it came from a chatbot that was told their channel's name.

---

## 2. Core Design Principles

Rules that override any individual implementation decision when they conflict:

1. **Fixed spine, swappable modules.** Pipeline stages are constant. What changes per genre is *which template or specialist* each stage uses — never the number of systems you maintain.
2. **Structured decisions, not free-text judgment calls.** Anywhere the system decides something (routing, planning, critique), the output is a schema, not prose — loggable, debuggable, testable.
3. **Typed contracts between agents.** Every agent's input and output is a defined artifact, not a blob of text one agent hopes another interprets correctly. This is what makes agents independently testable and replaceable.
4. **Default-first.** Every customer has a default recipe from their Channel Profile. Deviating from it requires a signal in the brief, not a fresh judgment call every run.
5. **Bounded loops.** Every feedback loop has a hard iteration cap. Unbounded agent loops are a cost and reliability risk, not a quality feature.
6. **Measure, don't eyeball.** Prompt and pipeline changes are evaluated against a fixed test set, not judged by reading a few outputs and feeling good about them.
7. **Validate before you generalize.** Don't build the Planner, specialist library, or Pipeline Builder until the core pipeline alone is proven to beat a strong single prompt.

---

## 3. System Architecture

```
┌───────────────────────────────────────────────────┐
│  META LAYER                                        │
│  Channel DNA · Planner · Orchestrator               │
└──────────────────┬──────────────────────────────────┘
                    │ structured plan
                    ▼
┌───────────────────────────────────────────────────┐
│  CORE PIPELINE (fixed spine)                        │
│  Research → Angle → Outline → Draft →                │
│  Critic loop → Fact-check → Voice → Visual           │
│  (each stage consumes/produces a typed Artifact)     │
└──────────────────┬──────────────────────────────────┘
                    │ specialists inserted per plan
                    ▼
┌───────────────────────────────────────────────────┐
│  SPECIALIST LIBRARY (genre-conditional)              │
│  Comic-Timing · Tension-Pacing · Rigor-Check · ...    │
└───────────────────────────────────────────────────┘

   Cross-cutting, touching every layer:
   ── Evaluation Framework (offline, tests prompt/pipeline changes)
   ── Execution & Observability (tracing every run, always on)
```

---

## 4. Artifact Specification

The typed objects agents pass between each other. This is the contract layer — get this right and agents become independently buildable, testable, and replaceable; get it wrong and every pipeline change risks silently breaking a downstream agent.

```
Dossier {
  topic: string
  facts: Fact[]            // { claim, source_ref, confidence }
  mechanisms: string[]      // how things work, causal chains
  misconceptions: string[]
  surprising_details: string[]
  open_questions: string[]  // things research couldn't confirm
}

Angle {
  thesis: string             // the one-sentence "why this matters"
  audience_hook: string      // why THIS audience, specifically
  discarded_angles: string[] // logged for traceability, not reuse
}

Outline {
  template_used: string      // e.g. "tension-arc-v1"
  beats: Beat[]              // { id, purpose, summary, open_loop? }
}

Draft {
  version: int
  body: string
  beat_refs: map<beat_id, text_span>   // traceability back to Outline
}

CriticReport {
  rubric_used: string
  pass: bool
  notes: CriticNote[]        // { line_ref, issue, suggested_fix }
  iteration: int
}

FactCheckReport {
  flags: Flag[]               // { claim, draft_ref, dossier_ref | "UNSOURCED" }
  pass: bool
}

VoiceReport {
  drift_flags: DriftFlag[]    // { line_ref, expected_tone, observed_tone }
  pass: bool
}

VisualBeatSheet {
  beats: VisualBeat[]          // { line_ref, direction, asset_type }
}

Plan {                          // Planner Agent output
  run_id: string
  outline_template: string
  specialists: string[]
  critic_rubric: string
  deviated_from_default: bool
  deviation_reason: string | null
  confidence: float
}
```

Every artifact carries enough back-references (`beat_ref`, `draft_ref`, `dossier_ref`) that you can always trace a line in the final script back to the research claim or outline beat that produced it. This traceability is what makes both fact-checking and debugging possible — without it, "why did the script say this" has no answer.

---

## 5. Meta Layer

| Component | Type | Responsibility |
|---|---|---|
| **Channel DNA Store** | Data | See Section 8 — the durable per-customer profile |
| **Onboarding Agent** | Agent | Builds initial Channel DNA from questionnaire + uploaded example scripts |
| **Planner Agent** | Agent (narrow) | Default recipe + this brief → a `Plan` artifact. Never executes anything itself |
| **Orchestrator** | Code | Executes the plan deterministically, enforces caps, emits traces (Section 9) |

---

## 6. Core Pipeline Agents

| Stage | Agent | Consumes | Produces |
|---|---|---|---|
| 1 | Research Agent (+ Paper-Comprehension variant) | Brief | `Dossier` |
| 2 | Angle Agent | `Dossier` + Channel DNA | `Angle` |
| 3 | Outline Agent | `Dossier` + `Angle` + template | `Outline` |
| 4 | Drafting Agent | `Outline` | `Draft` |
| 5 | Retention Critic Agent | `Draft` + rubric | `CriticReport` → redraft loop (cap: 2) |
| 6 | Fact-Check Agent | `Draft` + `Dossier` | `FactCheckReport` |
| 7 | Voice-Consistency Agent | `Draft` + Channel DNA | `VoiceReport` |
| 8 | Visual-Beat Agent | Final `Draft` | `VisualBeatSheet` |

---

## 7. Specialist Library

| Specialist | Genre trigger | Job |
|---|---|---|
| Comic-Timing Agent | Comedy/filmmaking-style | Joke placement, misdirection, callback setup, line rhythm |
| Tension-Pacing Agent | Horror/serious | Dread escalates, no premature release |
| Rigor-Check Agent | Research-paper dissection | Simplifications don't cross into inaccuracy |
| *(future)* | Added per validated demand | New genre = one template + usually one specialist |

---

## 8. Channel DNA / Brand Memory

The system's durable model of who it's writing for — elevated to a first-class pillar because it's the actual moat: pipeline architecture is replicable, an accurate per-customer style model built from real usage is not.

**Contains:**
```
ChannelDNA {
  customer_id
  niche: string
  genre_format: enum | custom
  tone_descriptors: string[]
  target_length_minutes: int
  audience: { region, language, age_range? }
  banned_words: string[]
  banned_topics: string[]
  example_scripts: [file refs]
  default_recipe: { outline_template, specialists[], critic_rubric }
  style_signals: StyleSignal[]   // inferred, see below
  edit_history: EditRecord[]     // { run_id, diff, accepted/rejected, inferred_reason? }
}
```

**How it's built and how it learns (the part v0.1 left as an open question — resolved here):**
- **Cold start:** Onboarding Agent infers initial `style_signals` from uploaded example scripts (sentence rhythm, vocabulary level, joke density, pacing) plus explicit questionnaire answers. Confidence on inferred signals starts low.
- **Ongoing:** every accepted/rejected edit in `edit_history` is a training signal. A lightweight periodic job (not a real-time agent — this doesn't need to run per-script) re-derives `style_signals` from accumulated edits and adjusts `default_recipe` when confidence crosses a threshold.
- **Guardrail:** style drift from edits should require a minimum sample size before changing the default recipe — a single unusual edit shouldn't retrain the profile. Log the *reason* for edits where inferable (tone / factual / pacing / preference) so the signal is diagnostic, not just "something changed."

This section is functionally the same store as v0.1's Channel Profile — the change is treating it as core IP from day one rather than a Phase 4 afterthought, and specifying the inference mechanism instead of leaving it open.

---

## 9. Evaluation Framework

Distinct from the in-flight Critic Agent (which judges one script) and from business metrics (Section 12). This is what tells you whether a *change to the system* helped or hurt — without it, every prompt edit is a guess.

**v1 scope (deliberately lightweight):**
- **Golden set:** 10–20 fixed test briefs spanning your launch genres, each with a rubric of what a good output looks like (specific, checkable criteria — not "is this good").
- **Regression check:** any change to an agent's prompt, model, or the pipeline shape gets run against the golden set before shipping. Compare against the previous baseline run, not just an absolute score.
- **Scoring:** a mix of automated checks (does `FactCheckReport` pass, does `CriticReport` pass, length within target) and periodic human spot-review — full automation of "is this actually good" isn't realistic at v1.
- **What NOT to build yet:** a general-purpose eval platform, statistical significance testing, or crowd-sourced rating. That's justified once you have enough volume and enough on the line to need it — not before Phase 0 is even validated.

**Why this can't wait:** without a golden set, you will not be able to tell, three months in, whether your tenth prompt tweak improved things or just changed things. That ambiguity is expensive.

---

## 10. Execution & Observability

Always-on infrastructure, not a feature — this is what makes the system debuggable once it's running in production instead of on your machine.

**Every run must log (the `Run` trace):**
```
Run {
  run_id
  customer_id
  plan: Plan
  prompt_versions: map<agent_name, version_id>   // exact prompt version per agent, per run
  model_versions: map<agent_name, model_id>
  stage_outputs: map<stage_name, Artifact>
  stage_latency_ms: map<stage_name, int>
  stage_cost: map<stage_name, float>
  redraft_iterations: int
  flagged_for_review: bool
  final_output: Draft
}
```

**Non-negotiables:**
- **Prompt versioning:** every agent prompt is versioned; every run records exactly which version produced it. Without this, a quality regression is archaeology instead of a git diff.
- **Cost/latency per stage, not just per run.** You need to know if the Critic loop is the expensive part or the Research stage is — aggregate numbers hide this.
- **Full trace retrievability:** given a `run_id`, you can reconstruct every artifact at every stage. This is what makes customer complaints ("why did it write this") answerable in minutes instead of unreproducible.

---

## 11. Quality Mechanics

- **Redraft loop:** Drafting Agent ↔ Retention Critic Agent, using `CriticReport`'s line-referenced notes for targeted redrafts, not vague re-prompts. Cap at 2 iterations, then ship with `flagged_for_review = true`.
- **Fact-check is adversarial by design:** a separate agent from Drafting, so it isn't the same "mind" that wrote the smooth sentence checking whether it's true.
- **Genre-aware rubrics:** the Critic's rubric is a parameter (from the `Plan`), not hardcoded logic.
- **Voice-consistency check runs last**, against the final draft, not an intermediate one.

---

## 12. Build Roadmap

**Phase 0 — Prove the core thesis**
Core pipeline (Section 6, stages 1–6), one genre, no Planner, no specialists. Channel DNA as a static onboarding form (skip the learning loop for now). **Also build the Artifact Specification and a minimal Evaluation golden set before writing agent prompts** — these are cheap now and define what "working" means for everything after. Do not proceed until this pipeline beats a strong single prompt on the golden set.

**Phase 1 — Round out the core**
Add Voice-Consistency and Visual-Beat agents. Add Execution & Observability properly (prompt versioning, full run tracing) — you want this in place before, not after, you start iterating heavily on prompts. Add a second genre manually (if/else routing) to stress-test the "fixed spine, swappable template" assumption.

**Phase 2 — Dynamic routing + authoring**
Build the Planner Agent once if/else routing starts breaking on edge cases. Build the **Pipeline Builder** here too — an authoring layer for templates/recipes separate from code — since by this point you'll actually have multiple pipeline variations worth managing this way. Building it earlier, with one pipeline shape, would be solving a problem you don't have yet.

**Phase 3 — Specialist library**
Add Comic-Timing, Tension-Pacing, Rigor-Check — one at a time, driven by actual signed-up customers in those genres.

**Phase 4 — Channel DNA learning loop**
Activate the edit-history-driven style inference described in Section 8. Needs real usage volume to be worth building — highest long-term leverage, correctly sequenced last.

---

## 13. How You'll Know It's Working

- **Golden-set score trend** (Section 9) — the primary signal for "is the system improving," tracked per change, not per vibe.
- **Edit distance** between generated script and what the customer publishes — should trend down per customer as Channel DNA matures.
- **Redraft loop trigger rate** — persistent high rate means the Drafting Agent or rubric needs work, not just "run it again."
- **Human-review flag rate** — should trend down per customer over time.
- **Time-to-usable-script** vs. the customer's previous process — the actual value proposition being sold.

---

## 14. Open Questions to Resolve Before Building

- Is the MVP customer you (via the [[youtube-channel]] project) or external customers from day one? This changes how soon a real UI/onboarding flow is needed relative to the architecture work.
- Model choice per agent — likely not one model for everything (fact-checking wants strong grounding/citation behavior; drafting wants strong prose style).
- Pricing/usage model — per script, per seat, or usage-based on agent calls (affects how aggressively redraft loops can run economically).
- Human-review flag handling — who reviews flagged runs, and what's the SLA, once you have real customers depending on turnaround time?

---

*Version 0.2. Treat this as living — update it as Phase 0 results come in, since real output quality will surface assumptions worth revisiting.*
