from pydantic import Field

from storyos.artifacts.base import BaseArtifact


class ChannelDNA(BaseArtifact):
    """
    Defines the creative identity of the channel.

    This artifact is read-only during pipeline execution and is
    updated only by the offline learning system.
    """

    channel_name: str = Field(
        description="Name of the YouTube channel.",
    )

    mission: str = Field(
        description="Core mission of the channel.",
    )

    audience: str = Field(
        description="Target audience.",
    )

    value_proposition: str = Field(
        description="What differentiates this channel from others.",
    )

    storytelling_principles: list[str] = Field(
        default_factory=list,
        description="High-level storytelling principles.",
    )

    humor_principles: list[str] = Field(
        default_factory=list,
        description="Guidelines for humor and comic timing.",
    )

    writing_principles: list[str] = Field(
        default_factory=list,
        description="Writing style guidelines.",
    )

    banned_patterns: list[str] = Field(
        default_factory=list,
        description="Things the agents should never produce.",
    )

    favorite_devices: list[str] = Field(
        default_factory=list,
        description="Preferred storytelling techniques.",
    )

    intro_style: str = Field(
        description="Preferred opening style.",
    )

    ending_style: str = Field(
        description="Preferred ending style.",
    )

    pacing_style: str = Field(
        description="Desired pacing of videos.",
    )

    default_recipe: str = Field(
        description="Default planning recipe selected by the Planner.",
    )

    artifact_type: str = "channel_dna"