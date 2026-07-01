from typing import Literal, Union
from classes.dataclasses import Scenario


type ScenarioNamesType = Literal["refill", "appointment", "insurance", "urgent", "angry", "default"]
type PatientKeys = Literal["name", "age", "goal", "personality", "interruption_level", "instructions"]
type PatientType = dict[PatientKeys, Union[str, int, float]]
type PatientAutofillType = dict[ScenarioNamesType, PatientType]
type PatientInstructionsType = dict[ScenarioNamesType, str]
type ScenarioLibraryType = dict[ScenarioNamesType, Scenario]
