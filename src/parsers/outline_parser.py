from __future__ import annotations

import json
from uuid import uuid4

from storyos.artifacts import Beat, Outline


class OutlineParser:
    """
    Parses the Outline Agent's JSON response into a validated Outline
    artifact.

    Responsibilities
    ----------------
    - Decode JSON.
    - Validate the schema.
    - Assign StoryOS-managed IDs.
    - Return a typed Outline artifact.

    The LLM never generates IDs.
    """

    @staticmethod
    def parse(
        response: str,
        *,
        run_id: str,
    ) -> Outline:
        """
        Parse a model response into an Outline artifact.
        """

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Outline Agent returned invalid JSON."
            ) from exc

        beats = []

        for beat in data["beats"]:
            beats.append(
                Beat(
                    id=f"beat_{uuid4().hex}",
                    **beat,
                )
            )

        return Outline(
            id=f"outline_{uuid4().hex}",
            run_id=run_id,
            title=data["title"],
            beats=beats,
        )