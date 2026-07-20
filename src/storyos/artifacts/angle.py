from pydantic import Field

from storyos.artifacts.base import BaseArtifact


class Angle(BaseArtifact):
    """
    Defines the storytelling angle selected for the topic.
    """

    title: str = Field(
        description="Short name for the chosen storytelling angle.",
    )

    core_premise: str = Field(
        description="One-sentence description of the chosen angle.",
    )

    hook: str = Field(
        description="Opening hook for the story.",
    )

    why_this_angle: str = Field(
        description="Reason this angle was selected over alternatives.",
    )

    audience_takeaway: str = Field(
        description="What the audience should remember after watching.",
    )

    artifact_type : str = "angle"

    discarded_angles: list[str] = Field(
        default_factory=list,
        description=(
            "Brief descriptions of promising narrative angles that were "
            "considered but rejected, including a short reason."
        )
    )

    supporting_fact_refs: list[str] = Field(
        default_factory=list,
        description="References to the facts that support the chosen angle."
    )