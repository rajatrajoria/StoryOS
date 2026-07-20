from storyos.artifacts import (
    Angle,
    Beat,
    ChannelDNA,
    CriticNote,
    CriticReport,
    Draft,
    DriftFlag,
    Dossier,
    Fact,
    FactCheckReport,
    FeedbackBundle,
    FeedbackItem,
    FeedbackSource,
    Flag,
    Outline,
    Plan,
    Specialist,
    VisualBeat,
    VisualBeatSheet,
    VoiceReport,
    Severity,
    TextLocation
)


def test_artifact_pipeline():
    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    fact = Fact(
        id="fact_001",
        statement="Lift is generated due to pressure differences around the wing.",
        source="NASA",
        confidence=0.99,
    )

    dossier = Dossier(
        id="dossier_001",
        run_id="run_001",
        producer="ResearchAgent",
        topic="Why Airplanes Fly",
        executive_summary="Research summary.",
        facts=[fact],
        misconceptions=[
            "Engines alone keep airplanes in the air."
        ],
        interesting_insights=[
            "Modern aircraft glide surprisingly well."
        ],
        analogies=[
            "A spoon bends water flowing around it."
        ],
    )

    # ------------------------------------------------------------------
    # Angle
    # ------------------------------------------------------------------

    angle = Angle(
        id="angle_001",
        run_id="run_001",
        producer="AngleAgent",
        title="The Biggest Flying Illusion",
        core_premise="Flying isn't what people think.",
        hook="How does something this heavy stay up?",
        why_this_angle="Challenges intuition.",
        audience_takeaway="Understand lift intuitively.",
    )

    # ------------------------------------------------------------------
    # Outline
    # ------------------------------------------------------------------

    beat = Beat(
        id="beat_001",
        order=1,
        title="Cold Open",
        objective="Create curiosity.",
        summary="Introduce the paradox.",
        fact_refs=[fact.id],
    )

    outline = Outline(
        id="outline_001",
        run_id="run_001",
        producer="OutlineAgent",
        title="Why Airplanes Fly",
        beats=[beat],
    )

    # ------------------------------------------------------------------
    # Draft
    # ------------------------------------------------------------------

    draft = Draft(
        id="draft_001",
        run_id="run_001",
        producer="DraftAgent",
        title="Why Airplanes Fly",
        script="Imagine throwing a truck into the sky... How does something this heavy stay up?",
        beat_refs=[beat.id],
        iteration=1,
    )

    # ------------------------------------------------------------------
    # Critic
    # ------------------------------------------------------------------

    critic_note = CriticNote(
        id="critic_001",
        severity=Severity.MEDIUM,
        location=TextLocation(
            beat_ref=beat.id,
            line_ref=5,
            text_anchor="Imagine throwing a truck into the sky...",
        ),
        issue="Hook could be stronger.",
        recommendation="Increase tension before revealing the answer.",
    )

    critic_report = CriticReport(
        id="critic_report_001",
        run_id="run_001",
        producer="CriticAgent",
        draft_ref=draft.id,
        passed=False,
        overall_score=8.2,
        summary="Solid script with pacing issues.",
        notes=[critic_note],
    )

    # ------------------------------------------------------------------
    # Fact Check
    # ------------------------------------------------------------------

    flag = Flag(
        id="flag_001",
        severity=Severity.HIGH,
        location=TextLocation(
            beat_ref=beat.id,
            line_ref=8,
            text_anchor="Engines create lift.",
        ),
        claim="Engines create lift.",
        reason="Incorrect. This violates the facts in the Dossier.",
        supporting_fact_refs=[fact.id],
        recommendation="Explain lift using pressure differences instead.",
    )

    fact_report = FactCheckReport(
        id="fact_report_001",
        run_id="run_001",
        producer="FactCheckAgent",
        draft_ref=draft.id,
        passed=False,
        summary="One factual issue detected.",
        flags=[flag],
    )

    # ------------------------------------------------------------------
    # Voice
    # ------------------------------------------------------------------

    drift = DriftFlag(
        id="voice_001",
        severity=Severity.LOW,
        location=TextLocation(
            beat_ref=beat.id,
            line_ref=12,
            text_anchor="Imagine throwing a truck into the sky...",
        ),
        principle="Explain like a film.",
        observation="Feels slightly textbook-like.",
        recommendation="Use a stronger visual analogy.",
    )

    voice_report = VoiceReport(
        id="voice_report_001",
        run_id="run_001",
        producer="VoiceAgent",
        draft_ref=draft.id,
        passed=True,
        overall_score=9.4,
        summary="Voice is mostly aligned.",
        flags=[drift],
    )

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    feedback_item = FeedbackItem(
        id="feedback_001",
        source=FeedbackSource.CRITIC,
        source_ref=critic_note.id,
        severity=Severity.MEDIUM,
        location=critic_note.location,
        issue=critic_note.issue,
        recommendation=critic_note.recommendation,
    )

    feedback = FeedbackBundle(
        id="feedback_bundle_001",
        run_id="run_001",
        producer="Orchestrator",
        draft_ref=draft.id,
        iteration=1,
        meta_guidance=(
            "Overall structure is strong. "
            "Avoid large rewrites. "
            "Strengthen the hook, fix the factual issue, "
            "and preserve the existing voice."
        ),
        summary="Please revise the draft based on the following findings.",
        total_findings=1,
        items=[feedback_item],
    )

    # ------------------------------------------------------------------
    # Visual
    # ------------------------------------------------------------------

    visual = VisualBeat(
        id="visual_001",
        beat_ref=beat.id,
        line_refs=[1, 2],
        objective="Hook",
        visual_description="Slow-motion airplane takeoff.",
        visual_type="B-Roll",
        assets=["Airplane footage"],
        on_screen_text="How is this possible?",
        transition="Cut",
    )

    visual_sheet = VisualBeatSheet(
        id="visual_sheet_001",
        run_id="run_001",
        producer="VisualAgent",
        title="Why Airplanes Fly",
        beats=[visual],
    )

    # ------------------------------------------------------------------
    # Channel DNA
    # ------------------------------------------------------------------

    dna = ChannelDNA(
        id="dna_001",
        run_id="system",
        producer="LearningSystem",
        channel_name="Miravo",
        mission="Explain everything like a film.",
        audience="Curious learners",
        value_proposition="Entertainment + education.",
        storytelling_principles=["Story first"],
        humor_principles=["Relatable humor"],
        writing_principles=["Simple language"],
        banned_patterns=["Wikipedia tone"],
        favorite_devices=["Callbacks"],
        intro_style="Cold Open",
        ending_style="Strong callback",
        pacing_style="Fast",
        default_recipe="cinematic_v1",
    )

    # ------------------------------------------------------------------
    # Plan
    # ------------------------------------------------------------------

    specialist = Specialist(
        name="Humor Specialist",
        enabled=True,
        objective="Increase laughs.",
    )

    plan = Plan(
        id="plan_001",
        run_id="run_001",
        producer="PlannerAgent",
        outline_template="cinematic",
        critic_rubric="miravo_v1",
        revision_budget=2,
        specialists=[specialist],
    )

    # ------------------------------------------------------------------
    # Relationship Validation
    # ------------------------------------------------------------------

    # Research → Outline
    assert beat.fact_refs == [fact.id]

    # Outline → Draft
    assert draft.beat_refs == [beat.id]

    # Draft → Review Reports
    assert critic_report.draft_ref == draft.id
    assert fact_report.draft_ref == draft.id
    assert voice_report.draft_ref == draft.id

    # Review → Feedback
    assert feedback.draft_ref == draft.id
    assert feedback.items[0].source_ref == critic_note.id

    # TextLocation integrity
    assert critic_note.location.beat_ref == beat.id
    assert flag.location.beat_ref == beat.id
    assert drift.location.beat_ref == beat.id

    assert critic_note.location.text_anchor == "Imagine throwing a truck into the sky..."
    assert flag.location.text_anchor == "Engines create lift."

    # Feedback
    assert feedback.items[0].location == critic_note.location
    assert "Overall structure is strong" in feedback.meta_guidance

    # Visual
    assert visual.beat_ref == beat.id

    # Plan
    assert plan.specialists[0].enabled

    # Channel DNA
    assert dna.default_recipe == "cinematic_v1"

    # Dossier
    assert dossier.facts[0].id == fact.id

    # Angle
    assert angle.audience_takeaway == "Understand lift intuitively."

    # Outline
    assert outline.beats[0].id == beat.id

    # Visual Sheet
    assert visual_sheet.beats[0].beat_ref == beat.id