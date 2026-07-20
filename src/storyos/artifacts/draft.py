from pydantic import Field

from storyos.artifacts.base import BaseArtifact


class Draft(BaseArtifact):
    """
    First complete version of the script.
    """

    title: str = Field(
        description="Final title of the script.",
    )

    script: str = Field(
        description="Complete script in markdown/plain text.",
    )

    iteration: int = Field(
        ge=1,
        description="Revision number of this draft."
    )

    beat_refs: list[str] = Field(
        default_factory=list,
        description="Ordered beat IDs used while writing the draft.",
    )

    artifact_type: str = "draft"