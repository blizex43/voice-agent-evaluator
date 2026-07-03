import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from enums.dir import TRANSCRIPT_DIR
from util.paths import ensure_output_dir, get_incremented_file_dirs

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")



def serialize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    serialized = {}
    for key, value in metadata.items():
        if is_dataclass(value):
            serialized[key] = asdict(value)
        else:
            serialized[key] = value
    return serialized


def transcript_paths() -> Dict[str, Path]:
    ensure_output_dir(TRANSCRIPT_DIR)
    return get_incremented_file_dirs("report_", TRANSCRIPT_DIR, {"json": "json", "md": "md"})


def save_transcript(
    session_id: str,
    messages: List[Dict[str, str]],
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Path]:
    paths = transcript_paths()
    payload = {
        "session_id": session_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": serialize_metadata(metadata or {}),
        "messages": messages,
    }

    paths["json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Transcript: {session_id}",
        "",
        f"Updated: {payload['updated_at']}",
        "",
    ]

    for message in messages:
        role = message.get("role", "unknown").title()
        content = message.get("content", "").strip()
        if content:
            lines.extend([f"**{role}:** {content}", ""])

    paths["md"].write_text("\n".join(lines), encoding="utf-8")
    return paths
