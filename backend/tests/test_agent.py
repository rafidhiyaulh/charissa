from charissa.agent import Agent, extract_code
from charissa.llm.base import LLMProvider, Message


class FakeLLM(LLMProvider):
    def __init__(self, replies: list[str]):
        self._replies = iter(replies)

    def complete(self, messages: list[Message]) -> str:
        return next(self._replies)


class FakeExecutor:
    def __init__(self, results: list[dict]):
        self._results = iter(results)

    def run(self, code: str, timeout: float = 10.0) -> dict:
        return next(self._results)


def test_extract_code_pulls_python_block():
    text = "Here is the plan.\n```python\nprint(1)\n```"
    assert extract_code(text) == "print(1)"


def test_extract_code_returns_none_without_block():
    assert extract_code("just talking, no code here") is None


def test_ask_returns_on_success():
    llm = FakeLLM(["plan\n```python\nprint(2)\n```"])
    executor = FakeExecutor([{"stdout": "2\n", "traceback": ""}])
    agent = Agent(llm, executor)

    result = agent.ask("add two numbers")

    assert result.code == "print(2)"
    assert result.execution["stdout"] == "2\n"


def test_ask_retries_once_on_traceback_then_succeeds():
    llm = FakeLLM(
        [
            "plan\n```python\nraise ValueError()\n```",
            "fixed plan\n```python\nprint('ok')\n```",
        ]
    )
    executor = FakeExecutor(
        [
            {"stdout": "", "traceback": "ValueError"},
            {"stdout": "ok\n", "traceback": ""},
        ]
    )
    agent = Agent(llm, executor)

    result = agent.ask("do something")

    assert result.execution["stdout"] == "ok\n"


def test_ask_returns_without_executing_when_no_code():
    llm = FakeLLM(["just an answer, no code needed"])
    executor = FakeExecutor([])
    agent = Agent(llm, executor)

    result = agent.ask("what is pandas")

    assert result.code is None
    assert result.execution is None
