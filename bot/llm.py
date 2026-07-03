from groq import Groq
from enums.collections import credentials
from enums.logger import log_and_raise
from enums.model import model_name, model_temperature, streaming_enabled


class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=credentials["groq"]["api_key"])

    async def chat(self, messages, model=model_name):
        """
        messages format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
            {"role": "assistant", "content": "..."}
        ]
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=model_temperature,
                stream=streaming_enabled,
            )
        except Exception as exc:
            log_and_raise(exc, f"Groq chat completion failed for model {model}")

        try:
            return response.choices[0].message.content
        except (IndexError, AttributeError) as exc:
            log_and_raise(
                exc,
                f"Malformed Groq response for model {model} (missing choices/message)",
            )
