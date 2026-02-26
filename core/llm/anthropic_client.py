import os
from anthropic import Anthropic
from .base import BaseLLM

class AnthropicClient(BaseLLM):
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_response(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=kwargs.get("max_tokens", 4096),
            **kwargs
        )
        return response.content[0].text
