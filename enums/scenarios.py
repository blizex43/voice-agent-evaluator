from classes.dataclasses import Scenario, Patient
from structs.prompts import ScenarioLibraryType, ScenarioNamesType
from enums.lore_books import patient_autofill_enum
from typing import Union, Literal
import random

def scenario_builder(name: ScenarioNamesType) -> Scenario:
    scenario = patient_autofill_enum[name]
    return Scenario(
        patient=Patient(
            name=scenario["name"],
            age=scenario["age"],
            goal=scenario["goal"],
            personality=scenario["personality"],
            interruption_level=scenario["interruption_level"],
            voice_index=scenario["voice_index"]
        ),
        instructions=[scenario["instructions"]],
    )


def scenario_to_messages(scenario: Scenario) -> list[dict[str, str]]:
    persona = scenario.patient
    return [
        {
            "role": "patient",
            "content": (
                f"My name is {persona.name}. I am {persona.age}. "
                f"{persona.goal} I am {persona.personality}."
            ),
        },
        *[
            {"role": "patient", "content": scenario.instructions}
        ],
    ]

def get_random_scenario_name() -> ScenarioNamesType:
    return random.choice(list(scenario_lib))

def get_scenario(name: Union[ScenarioNamesType, Literal["random"]]) -> Scenario:
    if name == "random":
        name = get_random_scenario_name()
    if name not in scenario_lib:
        valid_names = ", ".join(sorted(scenario_lib))
        raise ValueError(f"Unknown scenario '{name}'. Valid scenarios: {valid_names}")
    return scenario_lib[name]


def build_all_scenarios() -> ScenarioLibraryType:
    return {name: scenario_builder(name) for name in patient_autofill_enum.keys()}

scenario_names: list[ScenarioNamesType] = [name for name in patient_autofill_enum.keys()]
scenario_lib: ScenarioLibraryType = build_all_scenarios()

SCENARIOS = [scenario_to_messages(scenario) for scenario in scenario_lib.values()]
