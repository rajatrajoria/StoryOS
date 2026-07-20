"""
Custom exceptions used throughout StoryOS.
"""

from __future__ import annotations


class StoryOSError(Exception):
    """
    Base exception for StoryOS.

    All custom exceptions inherit from this.
    """


class PipelineError(StoryOSError):
    """
    Raised when pipeline execution fails.
    """


class AgentExecutionError(StoryOSError):
    """
    Raised when an agent fails during execution.
    """


class LLMError(StoryOSError):
    """
    Raised when an LLM provider returns an unexpected response.
    """


class ProviderError(LLMError):
    """
    Raised when communication with an LLM provider fails.
    """


class ValidationError(StoryOSError):
    """
    Raised when an artifact fails validation after generation.
    """