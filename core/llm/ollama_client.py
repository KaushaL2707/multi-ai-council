import ollama
from .base import BaseLLM

class OllamaClient(BaseLLM):
    def __init__(self, model: str = "llama3"):
        self.model = model

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            **kwargs
        )
        return response['message']['content']
