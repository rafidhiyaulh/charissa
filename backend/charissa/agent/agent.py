import re
from dataclasses import dataclass

from charissa.executor.docker_executor import DockerExecutor
from charissa.llm.base import LLMProvider, Message

SYSTEM_PROMPT = """You are a helpful data analyst assistant.

For every request, briefly explain your plan in plain text, then write the
code that solves it in a single fenced ```python code block. Use `print` to
show any results the user should see. Only pandas, numpy, and matplotlib are
available."""

_CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def extract_code(text: str) -> str | None:
    match = _CODE_BLOCK.search(text)
    return match.group(1).strip() if match else None


@dataclass
class StepResult:
    reply: str
    code: str | None
    execution: dict | None


class Agent:
    def __init__(self, llm: LLMProvider, executor: DockerExecutor):
        self._llm = llm
        self._executor = executor
        self._history: list[Message] = [Message(role="system", content=SYSTEM_PROMPT)]

    def ask(self, user_message: str, max_attempts: int = 2) -> StepResult:
        self._history.append(Message(role="user", content=user_message))

        for attempt in range(max_attempts):
            reply = self._llm.complete(self._history)
            self._history.append(Message(role="assistant", content=reply))

            code = extract_code(reply)
            if code is None:
                return StepResult(reply=reply, code=None, execution=None)

            execution = self._executor.run(code)
            self._history.append(
                Message(
                    role="user",
                    content=f"Execution result:\nstdout: {execution['stdout']}\ntraceback: {execution['traceback']}",
                )
            )
            if not execution["traceback"] or attempt == max_attempts - 1:
                return StepResult(reply=reply, code=code, execution=execution)

    def close(self):
        self._executor.close()
