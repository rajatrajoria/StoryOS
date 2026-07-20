from __future__ import annotations

from typing import Any

from storyos.agents.base import Agent
from parsers.research_parser import ResearchParser
from storyos.prompts.research_prompt import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_user_prompt,
)
from storyos.artifacts import ChannelDNA, Dossier


class ResearchAgent(Agent):
    """
    Research Agent.
    """

    @property
    def name(self) -> str:
        return "research"

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def build_user_prompt(
        self,
        *,
        topic: str,
        channel_dna: ChannelDNA,
        target_word_count: int | None = None,
        **_: Any,  # <-- Accepts and ignores extra kwargs like run_id
    ) -> str:
        return build_user_prompt(
            topic=topic,
            channel_dna=channel_dna.model_dump(mode="json"),
            target_word_count=target_word_count,
        )

    def parse_response(
        self,
        response: str,
        *,
        run_id: str | None = None,  # <-- Default fallback
        **_: Any,
    ) -> Dossier:
        effective_run_id = run_id or self.trace.run_id

        return ResearchParser.parse(
            response=response,
            run_id=effective_run_id,
        )