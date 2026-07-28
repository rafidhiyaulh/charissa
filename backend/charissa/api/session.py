import uuid
from typing import Callable

from charissa.agent import Agent
from charissa.executor.docker_executor import DockerExecutor
from charissa.llm import GeminiProvider

AgentFactory = Callable[[], Agent]


def default_agent_factory() -> Agent:
    return Agent(GeminiProvider(), DockerExecutor())


class SessionManager:
    """Tracks one Agent (and its sandboxed executor) per chat session."""

    def __init__(self, agent_factory: AgentFactory = default_agent_factory):
        self._agent_factory = agent_factory
        self._sessions: dict[str, Agent] = {}

    def create(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = self._agent_factory()
        return session_id

    def get(self, session_id: str) -> Agent | None:
        return self._sessions.get(session_id)

    def close(self, session_id: str) -> bool:
        agent = self._sessions.pop(session_id, None)
        if agent is None:
            return False
        agent.close()
        return True
