import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import requests
from enums.collections import credentials
from enums.dir import RECORDING_DIR
from enums.logger import log_and_raise
from enums.strings import (
    DEFAULT_RECORDING_SID,
    FILE_EXT_JSON,
    FILE_EXT_MD,
    FILE_EXT_MP3,
    FILE_PREFIX_RECORDING,
    TWILIO_API_TIMEOUT_SECONDS,
)
from util.paths import ensure_output_dir, get_incremented_file_dirs


def recording_paths() -> Dict[str, Path]:
    ensure_output_dir(RECORDING_DIR)
    return get_incremented_file_dirs(
        parent_dir=RECORDING_DIR,
        extensions={
            FILE_EXT_JSON: FILE_EXT_JSON,
            FILE_EXT_MD: FILE_EXT_MD,
            "audio": FILE_EXT_MP3,
        },
        prefix=FILE_PREFIX_RECORDING,
    )


def _write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        log_and_raise(exc, f"Failed to write text file {path}")


def _write_json(path: Path, payload: dict) -> None:
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        log_and_raise(exc, f"Failed to write JSON file {path}")

def _write_audio(path: Path, content: bytes) -> None:
    try:
        path.write_bytes(content)
    except OSError as exc:
        log_and_raise(exc, f"Failed to write audio file {path}")


def save_recording_metadata(form: Dict[str, str]) -> Dict[str, Path]:
    recording_sid = (
        form.get("RecordingSid") or form.get("CallSid") or DEFAULT_RECORDING_SID
    )
    paths = recording_paths()
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "call_sid": form.get("CallSid"),
        "recording_sid": form.get("RecordingSid"),
        "recording_status": form.get("RecordingStatus"),
        "recording_url": form.get("RecordingUrl"),
        "recording_duration": form.get("RecordingDuration"),
        "raw": form,
    }

    _write_json(paths[FILE_EXT_JSON], payload)

    lines = [
        f"# Recording: {recording_sid}",
        "",
        f"Updated: {payload['updated_at']}",
        f"Call SID: {payload['call_sid'] or ''}",
        f"Status: {payload['recording_status'] or ''}",
        f"Duration: {payload['recording_duration'] or ''}",
        f"URL: {payload['recording_url'] or ''}",
        "",
    ]
    _write_text(paths[FILE_EXT_MD], "\n".join(lines))
    return paths


def download_recording_audio(form: Dict[str, str]) -> Path | None:
    recording_url = form.get("RecordingUrl")
    recording_sid = form.get("RecordingSid")
    account_sid = credentials["twilio"]["account_sid"]
    auth_token = credentials["twilio"]["auth_token"]

    if not recording_url or not recording_sid or not account_sid or not auth_token:
        return None

    audio_url = (
        recording_url
        if recording_url.endswith(f".{FILE_EXT_MP3}")
        else f"{recording_url}.{FILE_EXT_MP3}"
    )
    audio_path = recording_paths()["audio"]
    try:
        response = requests.get(
            audio_url,
            auth=(account_sid, auth_token),
            timeout=TWILIO_API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        log_and_raise(exc, f"Failed to download recording audio from {audio_url}")

    _write_audio(audio_path, response.content)
    return audio_path
