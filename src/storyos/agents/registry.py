"""
Agent registry.

Responsible for registering and instantiating agents.
"""

from __future__ import annotations

from typing import Type

from storyos.agents.base import Agent


class AgentRegistry:
    """
    Registry for all StoryOS agents.
    """

    def __init__(self) -> None:
        self._agents: dict[str, Type[Agent]] = {}

    # ---------------------------------------------------------

    def register(
        self,
        agent_cls: Type[Agent],
    ) -> None:

        name = agent_cls.NAME

        if name in self._agents:
            raise ValueError(
                f"Agent '{name}' is already registered."
            )

        self._agents[name] = agent_cls

    # ---------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Type[Agent]:
        """
        Retrieve an agent class.
        """

        try:
            return self._agents[name]
        except KeyError as exc:
            raise ValueError(
                f"Unknown agent: '{name}'"
            ) from exc

    # ---------------------------------------------------------

    def create(
        self,
        name: str,
        **kwargs,
    ) -> Agent:
        """
        Instantiate an agent.
        """

        agent_cls = self.get(name)

        return agent_cls(**kwargs)

    # ---------------------------------------------------------

    def registered_agents(self) -> list[str]:
        """
        Return registered agent names.
        """

        return sorted(self._agents.keys())


registry = AgentRegistry()