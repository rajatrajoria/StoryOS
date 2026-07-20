from pprint import pprint

from dotenv import load_dotenv

from storyos.agents.angle_agent import AngleAgent
from storyos.agents.research_agent import ResearchAgent
from storyos.artifacts import ChannelDNA
from storyos.orchestrator import ModelClient, RunTrace

load_dotenv()


def main():
    print("=" * 80)
    print("Initializing StoryOS...")
    print("=" * 80)

    client = ModelClient()

    trace = RunTrace(
        run_id="demo_run",
        customer_id="local",
    )

    channel_dna = ChannelDNA(
        id="dna_001",
        run_id="system",
        producer="LearningSystem",
        channel_name="Miravo",
        mission="Explain everything like a film.",
        audience="Curious learners",
        value_proposition="Entertainment + Education",
        storytelling_principles=[
            "Story first",
            "Curiosity gap",
            "Hook the audience",
            "Surprise and delight",
        ],
        humor_principles=[
            "Heavy humor",
        ],
        writing_principles=[
            "Simple language",
        ],
        banned_patterns=[
            "Wikipedia tone",
        ],
        favorite_devices=[
            "Callbacks",
        ],
        intro_style="Cold Open",
        ending_style="Strong Callback",
        pacing_style="Fast",
        default_recipe="cinematic_v1",
        narration_wpm=145,
    )

    target_word_count = 500

    # ------------------------------------------------------------------
    # Research
    # ------------------------------------------------------------------

    research_agent = ResearchAgent(
        client=client,
        trace=trace,
    )

    print("\nRunning Research Agent...\n")

    dossier = research_agent.run(
        topic="Why airplanes fly",
        channel_dna=channel_dna,
        target_word_count=target_word_count,
    )

    print("=" * 80)
    print("DOSSIER")
    print("=" * 80)
    pprint(dossier.model_dump())

    print("\n")

    print("=" * 80)
    print("FACTS")
    print("=" * 80)

    for i, fact in enumerate(dossier.facts, start=1):
        print(f"\nFact {i}")
        print("-" * 40)
        pprint(fact.model_dump())

    # ------------------------------------------------------------------
    # Angle
    # ------------------------------------------------------------------

    angle_agent = AngleAgent(
        client=client,
        trace=trace,
    )

    print("\n")
    print("=" * 80)
    print("Running Angle Agent...")
    print("=" * 80)

    angle = angle_agent.run(
        dossier=dossier,
        channel_dna=channel_dna,
        target_word_count=target_word_count,
    )

    print("\n")

    print("=" * 80)
    print("ANGLE")
    print("=" * 80)
    pprint(angle.model_dump())

    # ------------------------------------------------------------------
    # Trace
    # ------------------------------------------------------------------

    print("\n")

    print("=" * 80)
    print("TRACE")
    print("=" * 80)

    pprint(trace)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    print("\n")

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"Cost           : ${trace.total_cost():.6f}")
    print(f"Latency        : {trace.total_latency_ms():.2f} ms")
    print(f"Input Tokens   : {trace.total_input_tokens()}")
    print(f"Output Tokens  : {trace.total_output_tokens()}")


if __name__ == "__main__":
    main()