import os

from google import genai
from google.genai import types

from charissa.llm.base import LLMProvider, Message

_ROLE_MAP = {"user": "user", "assistant": "model"}


class GeminiProvider(LLMProvider):
    def __init__(self, model: str = "gemini-2.5-flash", api_key: str | None = None):
        api_key = api_key or os.environ["GEMINI_API_KEY"]
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def complete(self, messages: list[Message]) -> str:
        system_prompt = "\n".join(m.content for m in messages if m.role == "system")
        contents = [
            types.Content(role=_ROLE_MAP[m.role], parts=[types.Part(text=m.content)])
            for m in messages
            if m.role != "system"
        ]
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_prompt or None),
        )
        return response.text
