from typing import Any, Dict, List, Optional
from .llm import LLMClient
from enums.prompts import initial_sys_prompt
from structs.custom import Message


class Conversation:
    def __init__(
        self,
        scenario: List[Message],
        session_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        self.scenario = scenario
        self.session_id = session_id
        self.metadata = metadata or {}
        self.history: List[Message] = []
        self.turn_index = 0
        # LLM client (Groq)
        self.llm = LLMClient()
        self.system_prompt = f"{initial_sys_prompt}\n Scenario: ${scenario}"
        print(self.system_prompt)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def next_patient_message(self) -> Optional[str]:
        if self.turn_index >= len(self.scenario):
            return None

        msg = self.scenario[self.turn_index]
        self.turn_index += 1

        return msg["content"]

    def agent_reply(self, patient_message: str) -> str:
        """
        REAL LLM CALL (Groq)
        """

        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # include last few messages for context (important for cost + performance)
        for m in self.history[-15:]:
            messages.append(m)

        # current patient input
        messages.append({"role": "user", "content": patient_message})
        return self.llm.chat(messages)

    def handle_patient_message(self, patient_message: str) -> str:
        agent_msg = self.agent_reply(patient_message)
        self.add_message("user", patient_message)
        self.add_message("assistant", agent_msg)
        return agent_msg

    def run(self):
        print("=== Conversation Start ===")

        while True:
            patient_msg = self.next_patient_message()

            if patient_msg is None:
                break

            print(f"Patient: {patient_msg}")

            agent_msg = self.handle_patient_message(patient_msg)

            print(f"Agent: {agent_msg}")

        print("=== Conversation End ===")
