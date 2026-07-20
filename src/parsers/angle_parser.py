from __future__ import annotations

import json
from uuid import uuid4

from storyos.artifacts import Angle


class AngleParser:
    """
    Parses the Angle Agent's JSON response into a validated Angle artifact.
    """

    @staticmethod
    def parse(
        *,
        response: str,
        run_id: str,
    ) -> Angle:
        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Angle Agent returned invalid JSON."
            ) from exc

        return Angle(
            id=f"angle_{uuid4().hex}",
            run_id=run_id,
            producer="AngleAgent",
            **data,
        )