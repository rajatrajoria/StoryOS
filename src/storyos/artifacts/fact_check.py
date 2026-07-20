from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact
from storyos.artifacts.common import Severity, TextLocation


class Flag(BaseModel):
    """
    A single factual issue identified in the draft.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this flag.",
    )

    severity: Severity = Field(
        description="Severity of the factual issue.",
    )

    claim: str = Field(
        description="The claim extracted from the draft.",
    )

    reason: str = Field(
        description="Why the claim was flagged.",
    )

    supporting_fact_refs: list[str] = Field(
        default_factory=list,
        description="Fact IDs from the Dossier supporting or contradicting this claim.",
    )

    recommendation: str = Field(
        description="Suggested correction or action.",
    )

    location: TextLocation = Field(
        description="Location of the issue in the draft."
    )


class FactCheckReport(BaseArtifact):
    """
    Report produced by the Fact Check Agent.
    """

    passed: bool = Field(
        description="Whether the draft passed factual verification.",
    )

    summary: str = Field(
        description="High-level summary of the fact-check results.",
    )

    flags: list[Flag] = Field(
        default_factory=list,
        description="List of factual issues found in the draft.",
    )

    draft_ref: str = Field(
        description="ID of the Draft evaluated."
    )

    artifact_type: str = "fact_check_report"