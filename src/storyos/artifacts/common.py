"""
Shared value objects for StoryOS.

Add models here ONLY when the same value object is required
by two or more domain artifacts.

Do not use this module as a generic dumping ground.
"""

from enum import Enum

from pydantic import BaseModel


class Severity(str, Enum):
    """
    Severity level assigned to review findings.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TextLocation(BaseModel):
    beat_ref: str
    line_ref: int | None = None
    text_anchor: str