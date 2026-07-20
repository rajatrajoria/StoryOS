from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact
from storyos.artifacts.common import Severity, TextLocation


class FeedbackSource(str, Enum):
    """
    Origin of a feedback item.
    """

    CRITIC = "critic"
    FACT_CHECK = "fact_check"
    VOICE = "voice"
    SPECIALIST = "specialist"


class FeedbackItem(BaseModel):
    """
    A normalized review finding produced by the Orchestrator.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this feedback item.",
    )

    source: FeedbackSource = Field(
        description="Originating review agent.",
    )

    source_ref: str = Field(
        description="ID of the original finding (CriticNote, Flag, DriftFlag, etc.).",
    )

    severity: Severity = Field(
        description="Severity of the issue.",
    )

    beat_ref: str | None = Field(
        default=None,
        description="Beat associated with the issue.",
    )

    line_ref: int | None = Field(
        default=None,
        description="Approximate line number in the draft.",
    )

    issue: str = Field(
        description="Description of the issue.",
    )

    recommendation: str = Field(
        description="Suggested fix.",
    )

    location: TextLocation = Field(
        description="Location of the issue in the draft."
    )
        



class FeedbackBundle(BaseArtifact):
    """
    Consolidated review feedback sent to the Draft Agent for revision.
    """

    iteration: int = Field(
        ge=1,
        description="Revision iteration number.",
    )

    summary: str = Field(
        description="High-level summary of the combined review.",
    )

    total_findings: int = Field(
        ge=0,
        description="Total number of feedback items.",
    )

    items: list[FeedbackItem] = Field(
        default_factory=list,
        description="Normalized feedback items.",
    )

    draft_ref: str = Field(
        description="Draft that should be revised."
    )

    meta_guidance: str | None = Field(
        default=None,
        description="Optional meta-guidance for the Draft Agent.",
    )

    artifact_type: str = "feedback_bundle"