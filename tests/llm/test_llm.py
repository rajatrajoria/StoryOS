from storyos.llm import get_client


def test_client_initialization():
    client = get_client()
    assert client is not None