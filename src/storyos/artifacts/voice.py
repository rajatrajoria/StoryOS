from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact
from storyos.artifacts.common import Severity, TextLocation


class DriftFlag(BaseModel):
    """
    A single deviation from the desired channel voice.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this drift flag.",
    )

    severity: Severity = Field(
        description="Severity of the voice drift.",
    )

    principle: str = Field(
        description="ChannelDNA principle that was violated.",
    )

    observation: str = Field(
        description="Description of the voice drift.",
    )

    recommendation: str = Field(
        description="Suggested correction.",
    )

    location: TextLocation = Field(
        description="Location of the issue in the draft."
    )


class VoiceReport(BaseArtifact):
    """
    Report produced by the Voice Agent.
    """

    passed: bool = Field(
        description="Whether the draft aligns with the ChannelDNA.",
    )

    overall_score: float = Field(
        ge=0.0,
        le=10.0,
        description="Overall voice alignment score.",
    )

    summary: str = Field(
        description="High-level summary of the voice review.",
    )

    flags: list[DriftFlag] = Field(
        default_factory=list,
        description="Detected voice deviations.",
    )
    
    draft_ref: str = Field(
        description="ID of the Draft evaluated."
    )

    artifact_type: str = "voice_report"