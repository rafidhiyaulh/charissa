import pytest

from charissa.executor.docker_executor import DockerExecutor


@pytest.fixture
def executor():
    ex = DockerExecutor()
    yield ex
    ex.close()


def test_state_persists_across_runs(executor):
    executor.run("x = 1 + 1")
    result = executor.run("print(x)")
    assert result["stdout"].strip() == "2"
    assert result["traceback"] == ""


def test_error_is_captured_as_traceback(executor):
    result = executor.run("1 / 0")
    assert "ZeroDivisionError" in result["traceback"]


def test_network_is_disabled(executor):
    result = executor.run(
        "import urllib.request\nurllib.request.urlopen('http://example.com', timeout=2)"
    )
    assert result["traceback"] != ""
