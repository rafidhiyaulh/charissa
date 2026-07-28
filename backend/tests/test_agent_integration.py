import os

import pytest
from dotenv import load_dotenv

from charissa.agent import Agent
from charissa.executor.docker_executor import DockerExecutor
from charissa.llm import GeminiProvider

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set",
)


def test_agent_answers_a_simple_computation():
    executor = DockerExecutor()
    try:
        agent = Agent(GeminiProvider(), executor)
        result = agent.ask("Using python, print the sum of 2 and 3.")
        assert result.execution is not None
        assert "5" in result.execution["stdout"]
    finally:
        executor.close()
