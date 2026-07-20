from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact


class Beat(BaseModel):
    """
    A single story beat in the narrative.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this beat.",
    )

    order: int = Field(
        ge=1,
        description="Position of the beat in the story.",
    )

    title: str = Field(
        description="Short title of the beat.",
    )

    objective: str = Field(
        description="Purpose of this beat in the story.",
    )

    summary: str = Field(
        description="Brief description of what happens in this beat.",
    )

    fact_refs: list[str] = Field(
        default_factory=list,
        description="IDs of supporting facts from the Dossier.",
    )

    target_word_count: int = Field(
        gt=0,
        description="Approximate word budget for this beat."
    )

    transition_to_next: str = Field(
        description="How this beat leads into the next beat.",
    )


class Outline(BaseArtifact):
    """
    High-level story structure.
    """

    title: str = Field(
        description="Working title of the story.",
    )

    beats: list[Beat] = Field(
        description="Ordered sequence of story beats.",
    )

    artifact_type: str = "outline"