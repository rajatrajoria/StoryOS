from __future__ import annotations

import json
import uuid
from typing import Any

from pydantic import ValidationError

from storyos.artifacts import Dossier, Fact


class ResearchParser:
    """
    Converts the raw LLM response into a validated Dossier artifact.

    Responsibilities
    ----------------
    - Parse JSON.
    - Validate required fields.
    - Construct Fact artifacts.
    - Generate Fact IDs.
    - Construct the final Dossier.

    This class contains no model-calling logic.
    """

    @classmethod
    def parse(
        cls,
        *,
        response: str,
        run_id: str,
    ) -> Dossier:
        """
        Parse a Research Agent response into a validated Dossier.
        """

        payload = cls._load_json(response)

        facts = cls._build_facts(
            payload.get("facts", [])
        )

        return Dossier(
            id=cls._generate_id("dossier"),
            run_id=run_id,
            producer="ResearchAgent",
            topic=payload["topic"],
            executive_summary=payload["executive_summary"],
            facts=facts,
            misconceptions=payload.get(
                "misconceptions",
                [],
            ),
            interesting_insights=payload.get(
                "interesting_insights",
                [],
            ),
            analogies=payload.get(
                "analogies",
                [],
            ),
        )

    # ---------------------------------------------------------
    # Private Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _load_json(response: str) -> dict[str, Any]:
        """
        Parse the model response into a dictionary.
        """

        try:
            payload = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Research Agent returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Research response must be a JSON object."
            )

        return payload

    @classmethod
    def _build_facts(
        cls,
        raw_facts: list[dict[str, Any]],
    ) -> list[Fact]:
        """
        Convert JSON fact dictionaries into Fact artifacts.
        """

        facts: list[Fact] = []

        for raw in raw_facts:
            try:
                fact = Fact(
                    id=cls._generate_id("fact"),
                    statement=raw["statement"],
                    source=raw["source"],
                    confidence=raw["confidence"],
                )
            except (KeyError, ValidationError) as exc:
                raise ValueError(
                    f"Invalid Fact received from Research Agent:\n{raw}"
                ) from exc

            facts.append(fact)

        return facts

    @staticmethod
    def _generate_id(prefix: str) -> str:
        """
        Generate deterministic-looking artifact IDs.

        Example:
            fact_f13b8b4d
            dossier_a82d91fe
        """

        return f"{prefix}_{uuid.uuid4().hex[:8]}"