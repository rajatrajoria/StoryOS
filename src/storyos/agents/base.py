from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from src.storyos.agents.names import AgentName
from storyos.orchestrator.model_client import (
    DEFAULT_MODEL_MAP,
    ModelClient,
    ModelConfig,
)
from storyos.orchestrator.trace import RunTrace


class Agent(ABC):
    """
    Base class for all StoryOS agents.

    Every agent:
        - has a unique identifier
        - has a versioned system prompt
        - owns one model configuration
        - produces one typed artifact
    """

    NAME: ClassVar[AgentName]

    def __init__(
        self,
        *,
        client: ModelClient,
        trace: RunTrace,
        model_config: ModelConfig | None = None,
    ) -> None:
        self.client = client
        self.trace = trace

        self.model_config = (
            model_config
            if model_config is not None
            else DEFAULT_MODEL_MAP[self.name]
        )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Unique pipeline identifier.

        Example:
            research
            outline
            draft
        """
        return self.NAME.value

    @property
    @abstractmethod
    def prompt_version(self) -> str:
        """
        Prompt version.

        Example:
            research_v1
            draft_v2
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        System prompt used for this agent.
        """
        raise NotImplementedError

    # ---------------------------------------------------------
    # Prompt Construction
    # ---------------------------------------------------------

    @abstractmethod
    def build_user_prompt(
        self,
        **kwargs: Any,
    ) -> str:
        """
        Convert input artifacts into a user prompt.
        """
        raise NotImplementedError

    # ---------------------------------------------------------
    # Response Parsing
    # ---------------------------------------------------------

    @abstractmethod
    def parse_response(
        self,
        response: str,
        **kwargs: Any,
    ) -> Any:
        """
        Convert model output into a typed artifact.
        """
        raise NotImplementedError

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def run(
        self,
        **kwargs: Any,
    ) -> Any:
        """
        Executes the complete lifecycle of an agent.

            Inputs
                ↓
        build_user_prompt()
                ↓
        ModelClient.complete()
                ↓
        parse_response()
                ↓
        RunTrace.record_stage()
                ↓
            Typed Artifact
        """

        user_prompt = self.build_user_prompt(**kwargs)

        model_response = self.client.complete(
            system_prompt=self.system_prompt,
            user_content=user_prompt,
            model_config=self.model_config,
            prompt_version=self.prompt_version,
        )

        artifact = self.parse_response(
            model_response.content,
            **kwargs,
        )

        self.trace.record_stage(
            stage_name=self.name,
            prompt_version=self.prompt_version,
            artifact_id=artifact.id,
            response=model_response,
        )

        return artifact