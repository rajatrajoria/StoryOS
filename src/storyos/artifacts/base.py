from datetime import datetime, UTC
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class BaseArtifact(BaseModel):
    """
    Base class for all StoryOS artifacts.

    Every artifact exchanged between agents inherits from this class.
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this artifact.",
    )

    run_id: str = Field(
        description="Unique identifier for the current StoryOS execution.",
    )

    producer: str = Field(
        description="Agent responsible for producing this artifact.",
    )

    schema_version: str = Field(
        default="1.0.0",
        description="Version of the artifact schema.",
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the artifact was created.",
    )

    artifact_type: str = Field(
        description="Logical type of this artifact."
    )
    