from pydantic import BaseModel, ConfigDict, Field

from storyos.artifacts.base import BaseArtifact


class VisualBeat(BaseModel):
    """
    Visual instructions corresponding to a story beat.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        description="Unique identifier for this visual beat.",
    )

    beat_ref: str = Field(
        description="Reference to the corresponding Beat.",
    )

    line_refs: list[int] = Field(
        default_factory=list,
        description="Approximate draft line numbers covered by this visual.",
    )

    objective: str = Field(
        description="Purpose of the visual in the story.",
    )

    visual_description: str = Field(
        description="Detailed description of the visual to show.",
    )

    visual_type: str = Field(
        description="Type of visual (animation, b-roll, meme, diagram, stock footage, etc.).",
    )

    assets: list[str] = Field(
        default_factory=list,
        description="Suggested assets, references, or footage.",
    )

    on_screen_text: str | None = Field(
        default=None,
        description="Optional text displayed on screen.",
    )

    transition: str | None = Field(
        default=None,
        description="Suggested transition into the next visual.",
    )


class VisualBeatSheet(BaseArtifact):
    """
    Production-ready visual plan for the entire script.
    """

    title: str = Field(
        description="Title of the visual plan.",
    )

    beats: list[VisualBeat] = Field(
        default_factory=list,
        description="Ordered visual plan.",
    )

    artifact_type: str = "visual_beat_sheet"