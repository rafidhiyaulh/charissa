from fastapi.testclient import TestClient

from charissa.api.app import app, get_session_manager
from charissa.api.session import SessionManager
from charissa.agent import StepResult


class FakeAgent:
    def __init__(self):
        self.closed = False

    def ask(self, message, max_attempts=2):
        return StepResult(reply=f"echo: {message}", code="print(1)", execution={"stdout": "1\n", "traceback": ""})

    def close(self):
        self.closed = True


def _client():
    manager = SessionManager(agent_factory=FakeAgent)
    app.dependency_overrides[get_session_manager] = lambda: manager
    return TestClient(app), manager


def test_health_returns_ok():
    client, _ = _client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_session_returns_id():
    client, _ = _client()
    response = client.post("/sessions")
    assert response.status_code == 200
    assert "session_id" in response.json()


def test_chat_returns_agent_result():
    client, _ = _client()
    session_id = client.post("/sessions").json()["session_id"]

    response = client.post(f"/sessions/{session_id}/chat", json={"message": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "echo: hello"
    assert body["stdout"] == "1\n"


def test_chat_unknown_session_returns_404():
    client, _ = _client()
    response = client.post("/sessions/does-not-exist/chat", json={"message": "hi"})
    assert response.status_code == 404


def test_close_session_removes_it():
    client, manager = _client()
    session_id = client.post("/sessions").json()["session_id"]

    response = client.delete(f"/sessions/{session_id}")

    assert response.status_code == 200
    assert manager.get(session_id) is None


def test_close_unknown_session_returns_404():
    client, _ = _client()
    response = client.delete("/sessions/does-not-exist")
    assert response.status_code == 404
