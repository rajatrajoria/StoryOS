from functools import lru_cache
from openai import OpenAI
from storyos.config import get_settings


class _OpenAIClient:
    """Internal wrapper around the OpenAI SDK."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = OpenAI(
            api_key=settings.openai_api_key,
        )

    @property
    def client(self) -> OpenAI:
        return self._client


@lru_cache
def get_openai_client() -> OpenAI:
    """
    Returns a cached, singleton OpenAI client instance.
    """
    return _OpenAIClient().client