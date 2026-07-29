import time
import uuid
from typing import Callable

from charissa.agent import Agent
from charissa.executor.docker_executor import DockerExecutor
from charissa.llm import GeminiProvider

AgentFactory = Callable[[], Agent]
Clock = Callable[[], float]


def default_agent_factory() -> Agent:
    return Agent(GeminiProvider(), DockerExecutor())


class SessionManager:
    """Tracks one Agent (and its sandboxed executor) per chat session.

    Sessions are only ever created on demand, so without cleanup an idle
    visitor's sandbox container would run forever. `close_idle` lets the
    caller periodically sweep sessions that haven't been touched in a while.
    """

    def __init__(self, agent_factory: AgentFactory = default_agent_factory, clock: Clock = time.monotonic):
        self._agent_factory = agent_factory
        self._clock = clock
        self._sessions: dict[str, Agent] = {}
        self._last_active: dict[str, float] = {}

    def create(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = self._agent_factory()
        self._last_active[session_id] = self._clock()
        return session_id

    def get(self, session_id: str) -> Agent | None:
        agent = self._sessions.get(session_id)
        if agent is not None:
            self._last_active[session_id] = self._clock()
        return agent

    def close(self, session_id: str) -> bool:
        agent = self._sessions.pop(session_id, None)
        self._last_active.pop(session_id, None)
        if agent is None:
            return False
        agent.close()
        return True

    def close_idle(self, ttl_seconds: float) -> list[str]:
        now = self._clock()
        idle_ids = [sid for sid, last in self._last_active.items() if now - last > ttl_seconds]
        for session_id in idle_ids:
            self.close(session_id)
        return idle_ids
