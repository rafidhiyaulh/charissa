from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str


class LLMProvider(ABC):
    """Common interface every model backend (Gemini, OpenAI, Anthropic, ...) implements."""

    @abstractmethod
    def complete(self, messages: list[Message]) -> str:
        """Send a conversation and return the model's full text reply."""
        raise NotImplementedError
