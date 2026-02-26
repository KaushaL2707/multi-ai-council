from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
