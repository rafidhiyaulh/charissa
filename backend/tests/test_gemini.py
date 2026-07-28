import os

import pytest
from dotenv import load_dotenv

from charissa.llm import GeminiProvider, Message

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set",
)


def test_complete_returns_text():
    provider = GeminiProvider()
    reply = provider.complete([Message(role="user", content="Reply with just the word: pong")])
    assert "pong" in reply.lower()
