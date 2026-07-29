from charissa.api.session import SessionManager


class FakeAgent:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def _manager_with_fake_clock():
    fake_time = [0.0]
    manager = SessionManager(agent_factory=FakeAgent, clock=lambda: fake_time[0])
    return manager, fake_time


def test_close_idle_removes_sessions_past_ttl():
    manager, fake_time = _manager_with_fake_clock()
    session_id = manager.create()

    fake_time[0] = 1000.0
    closed_ids = manager.close_idle(ttl_seconds=500)

    assert closed_ids == [session_id]
    assert manager.get(session_id) is None


def test_close_idle_keeps_recently_active_sessions():
    manager, fake_time = _manager_with_fake_clock()
    session_id = manager.create()

    fake_time[0] = 100.0
    closed_ids = manager.close_idle(ttl_seconds=500)

    assert closed_ids == []
    assert manager.get(session_id) is not None


def test_get_refreshes_last_active_time():
    manager, fake_time = _manager_with_fake_clock()
    session_id = manager.create()

    fake_time[0] = 400.0
    manager.get(session_id)  # touches last_active

    fake_time[0] = 700.0
    closed_ids = manager.close_idle(ttl_seconds=500)  # only 300s since the touch

    assert closed_ids == []


def test_close_idle_calls_agent_close():
    manager, fake_time = _manager_with_fake_clock()
    session_id = manager.create()
    agent = manager.get(session_id)

    fake_time[0] = 1000.0
    manager.close_idle(ttl_seconds=500)

    assert agent.closed is True
