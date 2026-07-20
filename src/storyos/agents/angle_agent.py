from __future__ import annotations

from storyos.artifacts import Angle, ChannelDNA, Dossier
from parsers.angle_parser import AngleParser
from storyos.prompts.angle_prompt import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_user_prompt,
)

from .base import Agent


class AngleAgent(Agent):
    """
    StoryOS Angle Agent.

    The Angle Agent is responsible for selecting the single strongest
    narrative direction for a video.

    Inputs
    ------
    - Dossier
    - ChannelDNA
    - target_word_count

    Output
    ------
    - Angle

    Responsibilities
    ----------------
    - Choose one compelling narrative angle.
    - Ground the decision in the supplied research.
    - Adapt to the channel's identity.
    - Adapt the scope to the requested video length.
    - Never invent facts.
    """

    @property
    def name(self) -> str:
        return "angle"

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
        channel_dna: ChannelDNA,
        target_word_count: int,
        **kwargs,
    ) -> str:
        """
        Build the user prompt for the Angle Agent.
        """

        return build_user_prompt(
            dossier=dossier.model_dump(mode="json"),
            channel_dna=channel_dna.model_dump(mode="json"),
            target_word_count=target_word_count,
        )

    # ---------------------------------------------------------
    # Response Parsing
    # ---------------------------------------------------------
    def parse_response(
        self,
        response: str,
        **kwargs,
    ) -> Angle:
        """
        Parse the model response into a validated Angle artifact.
        """

        return AngleParser.parse(
            response=response,
            run_id=kwargs["run_id"],
        )