from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact
from storyos.artifacts.common import Severity, TextLocation


class CriticNote(BaseModel):
    """
    A single issue identified during script review.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this note.",
    )

    severity: Severity = Field(
        description="Severity of the issue.",
    )

    location: TextLocation = Field(
        description="Location of the issue in the draft."
    )

    issue: str = Field(
        description="Description of the issue.",
    )

    recommendation: str = Field(
        description="Suggested improvement.",
    )
    

class CriticReport(BaseArtifact):
    """
    Quality review produced by the Critic Agent.
    """

    passed: bool = Field(
        description="Whether the draft passed the critic review.",
    )

    overall_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall quality score.",
    )

    summary: str = Field(
        description="High-level summary of the review.",
    )

    notes: list[CriticNote] = Field(
        default_factory=list,
        description="Detailed review findings.",
    )

    draft_ref: str = Field(
        description="ID of the Draft evaluated."
    )

    artifact_type: str = "critic_report"