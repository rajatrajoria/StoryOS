# StoryOS — Complete Implementation Plan

**Starting point: an empty repository. Nothing else exists yet.**

This is the strict, in-order build plan. Every milestone lists what to build, why it exists (tying back to the spec), how to test it before moving on, and a hard exit criterion. Do not start a milestone before the previous one's exit criterion is genuinely true — that discipline is the entire point of building this in order instead of all at once.

---

## M(-1) — Repo & Environment Setup

Nothing here is StoryOS-specific yet — this is just making the repo capable of running any of it.

**Tasks:**
1. Initialize the repo properly: `git init`, add a `.gitignore` (Python defaults: `__pycache__`, `.env`, `*.pyc`, `venv/`).
2. Create the folder structure:
   ```
   storyos/
     artifacts/       # typed schemas — the contracts between agents
     agents/          # one file per pipeline stage
     orchestrator/     # model client, run trace, pipeline wiring
     eval/             # golden set + scoring
     templates/         # outline templates (per-genre beat structures)
     rubrics/          # critic rubrics (per-genre pass/fail criteria)
     tests/            # unit tests per agent + pipeline integration tests
   ```
3. Set up a virtual environment (`python -m venv venv`) and a `requirements.txt` with at minimum: `pydantic`, `anthropic`, `openai`, `pytest`, `python-dotenv`.
4. Create a `.env.example` (not `.env` — that's gitignored) listing required keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
5. Get real API keys for both providers and confirm each with a trivial "hello world" call outside the codebase (a throwaway script), so you know the keys work before wiring them into agents.
6. Write a one-paragraph `README.md` stub — expand it as you go, don't front-load it.

**Exit criterion:** `pip install -r requirements.txt` succeeds in a clean venv, and you've confirmed both API keys work with a trivial standalone call.

---

## M0 — Foundations: Typed Contracts & Plumbing

This is the layer everything else depends on. Get artifact shapes wrong here and every agent built on top inherits the mistake.

**Why this exists:** per the spec's Design Principle #3 — every agent's input/output is a defined artifact, not a text blob one agent hopes another interprets correctly. This is what makes agents independently testable and replaceable later.

**Tasks:**
1. **`artifacts/schemas.py`** — define every typed artifact as a Pydantic model:
   - `Fact`, `Dossier` (stage 1 output)
   - `Angle` (stage 2 output)
   - `Beat`, `Outline` (stage 3 output)
   - `Draft` (stage 4 output)
   - `CriticNote`, `CriticReport` (stage 5 output)
   - `Flag`, `FactCheckReport` (stage 6 output)
   - `DriftFlag`, `VoiceReport` (stage 7 output — Phase 1)
   - `VisualBeat`, `VisualBeatSheet` (stage 8 output — Phase 1)
   - `ChannelDNA` (meta layer — see Section 8 of the spec for full field list)
   - `Plan` (Planner output — Phase 2, but define the shape now since it's cheap and unblocks nothing to wait)
   - Every artifact with a back-reference field (`beat_refs`, `draft_ref`, `dossier_ref`, `line_ref`) — this traceability is non-negotiable; it's what lets you answer "why did the script say this" later.
2. **`orchestrator/model_client.py`** — a provider-agnostic wrapper:
   - `ModelConfig` dataclass: provider + model name
   - A `DEFAULT_MODEL_MAP` dict mapping agent name → `ModelConfig`, encoding your model-mix decision (Claude for drafting/prose-sensitive work, an independent provider for fact-check specifically so it isn't grading its own family's output, cheaper/faster models for structural judgments like outline/critic)
   - A `ModelClient` class with a `.complete(system_prompt, user_content, prompt_version)` method. Implement the real Anthropic and OpenAI SDK calls here — this is the one place provider-specific code should live; agents should never import a provider SDK directly.
3. **`orchestrator/trace.py`** — the `RunTrace` dataclass: `run_id`, `customer_id`, per-stage prompt versions, model versions, outputs, latency, cost, redraft count, review-flag. Implement `record_stage()` and `total_cost()`/`total_latency_ms()` helpers.
4. **`agents/base.py`** — abstract `Agent` base class: `name`, `prompt_version`, an abstract `system_prompt` property, an abstract `run()` method. Every concrete agent inherits this.
5. Write a throwaway script that instantiates each schema with dummy data and confirms it validates (Pydantic will raise on bad data — use this to catch typos in field types early).

**Exit criterion:** every schema in `artifacts/schemas.py` imports and instantiates without error, `ModelClient` can make one real completion call to each of your two providers (test with a trivial prompt — you're testing plumbing, not agent quality yet).

---

## M1 — Research + Angle Agents

**Why this order:** these two are upstream of everything else, and their quality determines the ceiling for every later stage — a weak Dossier makes a weak Angle inevitable, which makes a weak Outline inevitable.

**Tasks:**
1. **`agents/research.py`** — implement `ResearchAgent.run(brief: str) -> Dossier`:
   - Write the real system prompt: instruct the model to separate verified facts (with sources) from mechanisms, misconceptions, surprising details, and explicitly flagged open questions it couldn't confirm.
   - Decide how research actually gets facts — will this agent have live web search / retrieval tool access, or is it working from model knowledge only? (If retrieval, wire that tool now; this is a real scope decision, not a detail — a Research Agent without retrieval is much weaker for time-sensitive or niche topics.)
   - Parse the model's response into a `Dossier` object. Handle parse failures explicitly (retry once with a stricter format instruction, then fail loudly rather than silently returning a malformed object).
2. **`agents/angle.py`** — implement `AngleAgent.run(dossier: Dossier, channel_dna: ChannelDNA) -> Angle`:
   - System prompt should force the model to consider and reject alternative angles, not just produce one — log `discarded_angles` for real, don't leave it empty.
   - Test that the Angle output actually references the audience/tone fields in `channel_dna`, not just the topic — if it ignores the profile, the prompt needs work.
3. **Tests (`tests/test_research.py`, `tests/test_angle.py`):**
   - Run each agent against 2-3 real topics manually (not automated yet — you're reading output, not scoring it).
   - Specifically check: does every `Fact` have a real, checkable `source_ref`? Does the `Angle`'s thesis actually differ meaningfully from a generic restatement of the topic?

**Exit criterion:** you'd hand a Dossier + Angle pair to a human writer and trust them to start outlining from it without needing to redo the research themselves.

---

## M2 — Outline + Drafting Agents

**Tasks:**
1. **`templates/` folder** — before writing the Outline Agent, define your first template as data, not code: a file (e.g. `templates/documentary_5part.json`) describing the beat structure (hook, mechanism, complication, why-unresolved, close) with a purpose description for each beat. This is what later lets genre templates be swappable without touching agent code.
2. **`agents/outline.py`** — implement `OutlineAgent.run(dossier, angle, template: str) -> Outline`:
   - Load the named template file, pass its structure into the prompt as a hard constraint ("follow this exact beat structure").
   - Parse into `Outline`, with each `Beat` getting a stable `id` — later stages will reference these ids for traceability.
3. **`agents/drafting.py`** — implement `DraftingAgent.run(outline, channel_dna, prior_draft=None, critic_report=None) -> Draft`:
   - Two modes in one method: first-pass draft (no `prior_draft`) vs. redraft (with `prior_draft` + `critic_report` — the prompt must instruct the model to address every critic note specifically, not do a generic rewrite).
   - Track `beat_refs`: after generating the draft, map each outline beat id to the text span that covers it. This can be a second, smaller model call ("given this draft and this outline, map beat ids to line ranges") rather than trying to get it in the same generation pass.
4. **Tests:** generate one full first-pass draft from a real outline, read it start to finish. You're checking readability and voice-match here — not fact accuracy (that's M3) or retention pacing (also M3).

**Exit criterion:** a first-pass, unedited draft is something you wouldn't be embarrassed to show someone as a rough draft — readable, in-voice, structurally following the outline.

---

## M3 — Critic Loop + Fact-Check

**Why fact-check is separate from drafting, on a different model provider:** an agent checking its own family's output is a weaker adversarial check than a genuinely independent one — this is deliberate, not incidental.

**Tasks:**
1. **`rubrics/` folder** — define your first critic rubric as data (e.g. `rubrics/documentary_v1.json`): concrete, checkable pass/fail criteria specific to your genre (pacing checks, no dead air longer than X, hook doesn't open with a definition, etc.) — not vague "make it engaging" instructions.
2. **`agents/retention_critic.py`** — implement `RetentionCriticAgent.run(draft, rubric: str, iteration: int) -> CriticReport`:
   - Prompt must force line-referenced, specific notes with a concrete suggested fix per issue — reject any implementation that lets the model return vague feedback.
   - Return a clean boolean `passed`, not a score to interpret — the orchestrator's redraft loop depends on this being decisive.
3. **`agents/fact_check.py`** — implement `FactCheckAgent.run(draft, dossier) -> FactCheckReport`:
   - Prompt should explicitly instruct: flag claims that are subtly stronger or more specific than what the dossier supports, not just outright contradictions.
   - **Deliberately test this agent adversarially before trusting it**: take a real draft, manually inject a wrong or oversold claim, and confirm the agent catches it. If it doesn't catch an obvious planted error, the prompt isn't ready.
4. **Wire the redraft loop** in `orchestrator/pipeline.py` (the earlier scaffold already has this structure — implement against your now-real agents): critic runs, if fail, draft regenerates with the critic's notes, cap at 2 iterations, then flag for review rather than looping indefinitely.

**Exit criterion:** the critic loop measurably improves a draft from iteration 1 to iteration 2 — you should be able to point to specific issues that got fixed. Fact-check catches at least one deliberately-injected error in your adversarial test.

---

## M4 — First Full End-to-End Run

**Tasks:**
1. Run the complete Phase 0 pipeline (research → angle → outline → draft → critic loop → fact-check) on one real brief, start to finish, with zero manual intervention between stages.
2. Separately, generate output for the same brief using one strong single prompt (your best-effort "just ask an LLM to write this script" baseline).
3. Compare both outputs honestly. Not "does the pipeline output look fine" — specifically: is it *better* than the baseline, and can you articulate *why* (more accurate, better paced, more in-voice, better structured)?
4. Write this comparison down. This record is what M5's go/no-go decision rests on.

**Exit criterion — the real one:** the pipeline's output is meaningfully better than the single-prompt baseline, with a written-down reason why. If it isn't better, this is a stop-and-diagnose point — go back into M1-M3 and figure out which stage is underperforming before adding anything else. Do not proceed to M5 on a "probably fine" judgment.

---

## M5 — Golden Set Expansion & Go/No-Go

**Tasks:**
1. Expand `eval/golden_set.json` from your one brief to 10-20, spanning a few different topics within your single launch genre. Each brief needs its own rubric notes (what a good output specifically looks like for that brief).
2. Build a minimal scoring script (`eval/run_golden_set.py`): runs every brief through the pipeline, records whether `CriticReport.passed` and `FactCheckReport.passed` came back true, and logs the final draft for manual spot-review.
3. Run the full set. Do a manual read of at least a third of the outputs — automated pass/fail isn't a substitute for actually reading the scripts at this stage.
4. Make the explicit go/no-go call: proceed to Phase 1, or return to specific agents that are underperforming.

**Exit criterion:** a documented pass rate across the golden set, plus a real, written decision — not just "seems okay, let's keep going."

---

## M6 — Phase 1: Round Out the Core

**Tasks:**
1. **`agents/voice_consistency.py`** — implement `VoiceConsistencyAgent.run(draft, channel_dna) -> VoiceReport`. Runs against the *final* draft (after the critic loop and fact-check), not an intermediate one — you're checking the actual output that would ship.
2. **`agents/visual_beat.py`** — implement `VisualBeatAgent.run(draft) -> VisualBeatSheet`. For your documentary genre this maps to b-roll/diagram direction per line — build this against your existing "Visuals with AI" script-to-prompt tool's expected input format if you're feeding output into it.
3. **Real observability logging** — up to now `RunTrace` has been structurally present but cost/latency may have been stubbed at 0.0. Wire real per-call cost calculation (from each provider's token usage response) and confirm prompt versions are actually being recorded, not just structurally possible.
4. **Add a second genre manually** — pick your next genre (comedy/filmmaking-style is a good stress test since it's structurally the most different from documentary). Write its outline template and critic rubric as new data files. Route to it with a simple `if genre == "comedy": ...` in the orchestrator — no Planner yet.
5. Run both genres through their own golden sets.

**Exit criterion:** two genres both produce passing golden-set results using the *same* pipeline code — only the template and rubric data files differ. This is your first real proof that "fixed spine, swappable module" holds up in practice, not just in the spec document.

---

## M7 — Phase 2: Dynamic Routing

**Do not start this milestone on a calendar trigger.** Start it when the if/else genre routing from M6 genuinely starts straining — a mixed-genre brief you can't cleanly route, or a third/fourth genre making the if/else chain unwieldy. Starting this early is the over-engineering trap the spec explicitly warns against.

**Tasks:**
1. **`agents/planner.py`** — implement `PlannerAgent.run(channel_dna, brief) -> Plan`. Input: the channel's default recipe + this specific brief. Output: a structured `Plan` (outline template, specialists to insert, critic rubric, and whether/why it deviated from the default). This agent decides, it does not execute.
2. Update the orchestrator to consume a `Plan` and execute it deterministically — the Planner's job ends at producing the plan object.
3. **Pipeline Builder** — build the authoring layer that lets you define new templates/rubrics/recipes as data without touching orchestrator code. By this point you'll have enough real template variations to justify this; earlier it would have been solving a problem you didn't have yet.
4. Add plan logging to `RunTrace` and a confidence-based fallback: if the Planner's confidence is low, fall back to the channel's default recipe and flag for human review rather than let it guess at an unusual combination.

**Exit criterion:** the Planner correctly routes a genuinely ambiguous or mixed-signal brief (test this deliberately with a few edge-case briefs) without needing an if/else code change to handle it.

---

## M8 — Phase 3: Specialist Library

Built one at a time, each triggered by actual signed-up demand in that genre — not speculatively ahead of a real customer.

**Tasks, per specialist (repeat this shape for each):**
1. **`agents/comic_timing.py`** — `ComicTimingAgent.run(draft) -> CriticReport`-shaped output (or a dedicated report type if joke-specific feedback needs different fields than the generic critic). Checks joke placement, misdirection, callback setup, line rhythm. Insert into the pipeline only when the Planner's `Plan.specialists` includes it.
2. **`agents/tension_pacing.py`** — `TensionPacingAgent.run(draft) -> ...`. Checks that dread/tension escalates across the draft and doesn't release prematurely. This genuinely needs a different evaluation shape than comedy — likely a stage-by-stage tension curve check rather than line-by-line notes, so don't force it into the exact same report schema as Comic-Timing without checking it actually fits.
3. **`agents/rigor_check.py`** — `RigorCheckAgent.run(draft, dossier) -> ...`. For research-paper dissection channels: checks that simplifications haven't crossed into inaccuracy. This one overlaps conceptually with Fact-Check but is specifically about *simplification* risk, not sourcing — keep them distinct rather than merging, since a claim can be accurately sourced and still misleadingly oversimplified.
4. For each: write its own template/rubric data files, add it to the Planner's specialist-selection logic, add golden-set briefs specific to that genre, and don't consider it done until it passes its own golden set — not just "it runs without errors."

**Exit criterion (per specialist):** the specialist demonstrably catches issues the generic Retention Critic misses — test this by deliberately running a genre-appropriate draft with a planted timing/pacing/rigor problem through both, and confirming only the specialist catches it.

---

## M9 — Phase 4: Channel DNA Learning Loop

Needs real usage volume to be worth building — don't start this on a handful of test runs.

**Tasks:**
1. Instrument the product surface (however customers interact with output — UI edits, accept/reject actions) to actually populate `ChannelDNA.edit_history` with real diffs, not placeholder data.
2. Build the periodic (not real-time) job that re-derives `style_signals` from accumulated edit history — sentence rhythm, vocabulary level, pacing preferences inferred from what customers actually change.
3. Add the minimum-sample-size guardrail before this inference is allowed to change a customer's `default_recipe` — a single unusual edit should never retrain the profile.
4. Where inferable, log *why* an edit happened (tone / factual / pacing / preference) so the signal is diagnostic, not just "something changed."

**Exit criterion:** for a customer with a real edit history, the system's `default_recipe` demonstrably shifts in response to a consistent pattern of edits (test with a synthetic but realistic edit history if real customer volume isn't there yet) — and does *not* shift in response to a single one-off edit.

---

## How to use this document while building

- Work top to bottom. Resist the pull to jump ahead to a more interesting milestone (Planner and specialists are more fun to build than plumbing — that's exactly why the plan sequences them last).
- Every exit criterion is a checkpoint, not a suggestion. If you're tempted to skip one because "it's probably fine," that's the signal to actually check.
- Update this document as you go if reality diverges from the plan — a plan that doesn't get revised against what you actually learn while building isn't doing its job.