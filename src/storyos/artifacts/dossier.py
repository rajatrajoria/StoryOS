from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact


class Fact(BaseModel):
    """
    Atomic unit of factual knowledge.

    Every factual claim in StoryOS originates as a Fact inside a Dossier.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this fact.",
    )

    statement: str = Field(
        description="The factual claim.",
    )

    source: str = Field(
        description="Citation or source of the fact.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score assigned by the Research Agent.",
    )


class Dossier(BaseArtifact):
    """
    Research artifact.

    This is the single source of truth for all factual information
    used throughout the pipeline.
    """

    topic: str

    executive_summary: str

    facts: list[Fact]

    misconceptions: list[str] = Field(default_factory=list)

    interesting_insights: list[str] = Field(default_factory=list)

    analogies: list[str] = Field(default_factory=list)

    artifact_type: str = "dossier"