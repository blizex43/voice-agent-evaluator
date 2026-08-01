from typing import Literal, Union, Any
from classes.dataclasses import Scenario


type ScenarioNamesType = Literal["refill", "appointment", "insurance", "urgent", "angry", "default"]
type PatientKeys = Literal["name", "age", "goal", "personality", "interruption_level", "instructions", "voice_index"]
type BlacklistIndex = Literal["phrases", "suffix_word_limit"]
type PatientType = dict[PatientKeys, Union[str, int, float]]
type PatientAutofillType = dict[ScenarioNamesType, PatientType]
type PatientInstructionsType = dict[ScenarioNamesType, str]
type ScenarioLibraryType = dict[ScenarioNamesType, Scenario]
type BlacklistOptionsType = list[dict[BlacklistIndex, Any]]