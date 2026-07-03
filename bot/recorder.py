import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import requests
from enums.collections import credentials
from enums.dir import RECORDING_DIR
from util.paths import ensure_output_dir, get_incremented_file_dirs
def recording_paths() -> Dict[str, Path]:
    ensure_output_dir(RECORDING_DIR)
    return get_incremented_file_dirs("report_", RECORDING_DIR, {"json": "json", "md": "md", "audio": "mp3"})


def save_recording_metadata(form: Dict[str, str]) -> Dict[str, Path]:
    recording_sid = form.get("RecordingSid") or form.get("CallSid") or "unknown-recording"
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

    paths["json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")

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
    paths["md"].write_text("\n".join(lines), encoding="utf-8")
    return paths


def download_recording_audio(form: Dict[str, str]) -> Path | None:
    recording_url = form.get("RecordingUrl")
    recording_sid = form.get("RecordingSid")
    account_sid = credentials["twilio"]["account_sid"]
    auth_token = credentials["twilio"]["auth_token"]

    if not recording_url or not recording_sid or not account_sid or not auth_token:
        return None

    audio_url = recording_url if recording_url.endswith(".mp3") else f"{recording_url}.mp3"
    audio_path = recording_paths()["audio"]
    response = requests.get(audio_url, auth=(account_sid, auth_token), timeout=30)
    response.raise_for_status()
    audio_path.write_bytes(response.content)
    return audio_path
