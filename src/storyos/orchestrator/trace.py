"""
Observability and execution tracking for StoryOS runs.

Captures stage-by-stage latency, token usage, cost, and prompt versioning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .model_client import ModelResponse


# ============================================================
# Per-Stage Trace
# ============================================================


@dataclass(slots=True)
class StageTrace:
    """
    Trace information for a single pipeline stage.
    """

    stage_name: str
    prompt_version: str
    provider: str
    model: str
    latency_ms: float
    cost_usd: float
    input_tokens: int
    output_tokens: int
    artifact_id: str
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# Run Trace
# ============================================================


@dataclass(slots=True)
class RunTrace:
    """
    Complete trace for one StoryOS execution run.
    """

    run_id: str
    customer_id: str | None = None
    review_flag: bool = False
    redraft_count: int = 0
    stages: list[StageTrace] = field(default_factory=list)

    # --------------------------------------------------------

    def record_stage(
        self,
        *,
        stage_name: str,
        prompt_version: str,
        artifact_id: str,
        response: ModelResponse,
    ) -> None:
        """
        Record one completed stage and accurately calculate start/end timestamps.
        """
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(milliseconds=response.latency_ms)

        self.stages.append(
            StageTrace(
                stage_name=stage_name,
                prompt_version=prompt_version,
                provider=response.provider.value,
                model=response.model,
                latency_ms=response.latency_ms,
                cost_usd=response.estimated_cost_usd,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                artifact_id=artifact_id,
                started_at=start_time,
                completed_at=now,
            )
        )

    # --------------------------------------------------------

    def total_cost(self) -> float:
        """
        Total cost (USD) for the entire pipeline run.
        """
        return round(
            sum(stage.cost_usd for stage in self.stages),
            6,
        )

    # --------------------------------------------------------

    def total_latency_ms(self) -> float:
        """
        Total latency across all stages.
        """
        return round(
            sum(stage.latency_ms for stage in self.stages),
            2,
        )

    # --------------------------------------------------------

    def total_input_tokens(self) -> int:
        return sum(stage.input_tokens for stage in self.stages)

    # --------------------------------------------------------

    def total_output_tokens(self) -> int:
        return sum(stage.output_tokens for stage in self.stages)

    # --------------------------------------------------------

    def latest_stage(self, name: str) -> StageTrace | None:
        """
        Return the most recent trace for a stage if it exists.
        Useful when stages re-run during redrafts.
        """
        for stage in reversed(self.stages):
            if stage.stage_name == name:
                return stage
        return None

    # --------------------------------------------------------

    def stages_by_name(self, name: str) -> list[StageTrace]:
        """
        Return all traces for a specific stage name across iterations.
        """
        return [s for s in self.stages if s.stage_name == name]