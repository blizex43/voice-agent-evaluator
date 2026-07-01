from groq import Groq
from dotenv import load_dotenv
from enums.collections import credentials
from enums.model import model_name, model_temperature, streaming_enabled, max_tokens_generated
load_dotenv()


class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=credentials["groq"]["api_key"])

    def chat(self, messages, model=model_name):
        """
        messages format:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
        """

        response = self.client.chat.completions.create(
            model=model, messages=messages, temperature=model_temperature, stream=streaming_enabled
        )
        return response.choices[0].message.content
