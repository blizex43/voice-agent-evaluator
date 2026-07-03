from typing import Any, Dict, List, Optional
from .llm import LLMClient
from enums.logger import log_info
from enums.prompts import initial_sys_prompt, agent_title, user_title
from structs.custom import Message
from enums.model import max_history


def _build_system_prompt(
    scenario: List[Message], role: str, user_role: str
) -> str:
    """Compose the system prompt for the LLM given the scenario and role labels."""
    return (
        f"{initial_sys_prompt}\n"
        f"Your Role is {role}\n"
        f"User role is: {user_role}\n"
        f"Scenario: ${scenario}"
    )


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
        self.role = agent_title
        self.user_role = user_title
        self.turn_index = 0
        # LLM client (Groq)
        self.llm = LLMClient()
        self.system_prompt = _build_system_prompt(scenario, self.role, self.user_role)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def next_user_message(self) -> Optional[str]:
        if self.turn_index >= len(self.scenario):
            return None

        msg = self.scenario[self.turn_index]
        self.turn_index += 1

        return msg["content"]

    async def agent_reply(self, user_message: str) -> str:
        """
        REAL LLM CALL (Groq)
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        for m in self.history[-max_history:]:
            messages.append(m)

        # current patient input
        messages.append({"role": "user", "content": user_message})
        return await self.llm.chat(messages)

    async def handle_user_message(self, user_message: str) -> str:
        agent_msg = await self.agent_reply(user_message)
        self.add_message("user", user_message)
        self.add_message("assistant", agent_msg)
        return agent_msg

    def run(self):
        log_info("=== Conversation Start ===")

        while True:
            patient_msg = self.next_user_message()

            if patient_msg is None:
                break

            log_info(f"Patient: {patient_msg}")

            agent_msg = self.handle_user_message(patient_msg)

            log_info(f"Agent: {agent_msg}")

        log_info("=== Conversation End ===")
