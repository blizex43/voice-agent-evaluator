from dataclasses import dataclass
from typing import Iterable
from enums.collections import credentials, urls
from classes.dataclasses import ConfigCheck

COMMON_KEYS = [
    ConfigCheck("GROQ_API_KEY", credentials["groq"]["api_key"]),
]

TWILIO_KEYS = [
    ConfigCheck("TWILIO_ACCOUNT_SID", credentials["twilio"]["account_sid"]),
    ConfigCheck("TWILIO_AUTH_TOKEN", credentials["twilio"]["auth_token"]),
    ConfigCheck("TWILIO_PHONE_NUMBER", credentials["twilio"]["from_phone_number"]),
    ConfigCheck("TEST_NUMBER", credentials["twilio"]["to_phone_number"]),
    ConfigCheck("ENDPOINT_URL", urls["endpoint"]),
]


def missing_keys(checks: Iterable[ConfigCheck]) -> list[str]:
    return [check.name for check in checks if not check.value]


def validate_config(require_twilio: bool = False) -> None:
    checks = [*COMMON_KEYS]
    if require_twilio:
        checks.extend(TWILIO_KEYS)

    missing = missing_keys(checks)
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variable(s): {joined}")
