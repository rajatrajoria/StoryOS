from storyos.llm import get_openai_client

def test_client_initialization():
    client = get_openai_client()
    assert client is not None