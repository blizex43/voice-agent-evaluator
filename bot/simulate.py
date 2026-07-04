from bot.conversation import Conversation
from uuid import uuid4
from bot.analyzer import save_bug_report
from enums.strings import SIMULATION_SESSION_PREFIX
from structs.prompts import ScenarioNamesType
from enums.scenarios import get_scenario, scenario_to_messages
from bot.transcript import save_transcript
def build_simulation_session_id(scenario_name: ScenarioNamesType) -> str:
    """Compose a unique session id for a simulation run."""
    return f"{SIMULATION_SESSION_PREFIX}{scenario_name}-{uuid4().hex[:8]}"


def run_simulation(scenario_name: ScenarioNamesType) -> None:
    scenario = get_scenario(scenario_name)
    session_id = build_simulation_session_id(scenario_name)
    conversation = Conversation(
        scenario_to_messages(scenario),
        session_id=session_id,
        metadata={"mode": "simulation", "scenario": scenario},
    )

    conversation.run()
    transcript_paths = save_transcript(
        session_id, conversation.history, conversation.metadata, conversation.id
    )
    report_paths = save_bug_report(session_id, conversation.history, conversation.id)

    print(f"Transcript: {transcript_paths['md']}")
    print(f"Bug report: {report_paths['md']}")