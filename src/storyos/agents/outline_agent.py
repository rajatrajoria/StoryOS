from __future__ import annotations
from typing import Any

from storyos.artifacts import (
    Angle,
    ChannelDNA,
    Dossier,
    Outline,
)
from parsers.outline_parser import OutlineParser
from storyos.prompts.outline_prompt import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_user_prompt,
)

from .base import Agent


class OutlineAgent(Agent):
    """
    StoryOS Outline Agent.

    The Outline Agent transforms research and the selected narrative
    angle into a complete story blueprint.

    Inputs
    ------
    - Dossier
    - Angle
    - ChannelDNA
    - target_word_count

    Output
    ------
    - Outline

    Responsibilities
    ----------------
    - Design the narrative structure.
    - Allocate story beats.
    - Assign word budgets.
    - Maintain narrative flow.
    - Preserve factual traceability.
    """

    @property
    def name(self) -> str:
        return "outline"

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    # ---------------------------------------------------------
    # Prompt Construction
    # ---------------------------------------------------------

    def build_user_prompt(
        self,
        *,
        dossier: Dossier,
        angle: Angle,
        channel_dna: ChannelDNA,
        target_word_count: int,
        **_: Any,  # <-- Safely ignores unexpected execution kwargs
    ) -> str:
        """
        Build the user prompt for the Outline Agent.
        """

        return build_user_prompt(
            dossier=dossier.model_dump(mode="json"),
            angle=angle.model_dump(mode="json"),
            channel_dna=channel_dna.model_dump(mode="json"),
            target_word_count=target_word_count,
        )

    # ---------------------------------------------------------
    # Response Parsing
    # ---------------------------------------------------------

    def parse_response(
        self,
        response: str,
        *,
        run_id: str | None = None,  # <-- Default fallback
        **_: Any,  # <-- Safely absorbs 'dossier', 'channel_dna', etc. passed by Agent.run()
    ) -> Outline:
        """
        Parse the model response into an Outline artifact.
        """
        effective_run_id = run_id or self.trace.run_id
        return OutlineParser.parse(
            response,
            run_id=effective_run_id,
        )