from dataclasses import dataclass
from typing import List


@dataclass
class Patient:
    name: str
    age: int
    goal: str
    personality: str  # e.g. "anxious", "angry", "calm"
    interruption_level: float = 0.0  # 0.0 → 1.0


@dataclass
class Scenario:
    patient: Patient
    instructions: str

@dataclass(frozen=True)
class ConfigCheck:
    name: str
    value: str | None
