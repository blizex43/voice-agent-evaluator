from groq import Groq
from enums.collections import credentials
from enums.model import model_name, model_temperature, streaming_enabled
class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=credentials["groq"]["api_key"])

    def chat(self, messages, model=model_name):
        """
        messages format:
        [
            "{""role": "system", "content": "..."},
            {"role": "{user_title}", "content": "..."}
            {"role": "{agent_title}", "content": "..."}
        ]
        """
        print(messages)
        response = self.client.chat.completions.create(
            model=model, messages=messages, temperature=model_temperature, stream=streaming_enabled
        )
        return response.choices[0].message.content
