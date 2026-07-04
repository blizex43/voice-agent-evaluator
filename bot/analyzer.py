import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from enums.bug_rules import BUG_RULES
from enums.dir import REPORT_DIR
from enums.logger import log_and_raise
from enums.strings import FILE_EXT_JSON, FILE_EXT_MD, FILE_PREFIX_REPORT
from util.paths import get_incremented_file_dirs, ensure_output_dir

def _contains_any(text: str, terms: List[str]) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in terms)


def detect_bugs(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    bugs = []
    full_assistant_text = " ".join(
        message["content"] for message in messages if message.get("role") == "assistant"
    )

    for rule in BUG_RULES:
        if rule.get("conversation_level"):
            has_expected_assistant_text = _contains_any(
                full_assistant_text, rule["assistant_terms"]
            )
            if rule.get("inverse") and not has_expected_assistant_text:
                bugs.append(
                    {
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "evidence": "No matching assistant identity-collection language found.",
                    }
                )
            continue

        for index, message in enumerate(messages):
            if message.get("role") != "user":
                continue

            patient_text = message.get("content", "")
            if rule["patient_terms"] and not _contains_any(
                patient_text, rule["patient_terms"]
            ):
                continue

            next_assistant = ""
            for followup in messages[index + 1 :]:
                if followup.get("role") == "assistant":
                    next_assistant = followup.get("content", "")
                    break

            has_expected_assistant_text = _contains_any(
                next_assistant, rule["assistant_terms"]
            )
            if not has_expected_assistant_text:
                bugs.append(
                    {
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "evidence": patient_text,
                    }
                )
                break

    return bugs


def report_paths(index: int = None) -> Dict[str, Path]:
    ensure_output_dir(REPORT_DIR)
    return get_incremented_file_dirs(
        parent_dir=REPORT_DIR,
        extensions={FILE_EXT_JSON: FILE_EXT_JSON, FILE_EXT_MD: FILE_EXT_MD},
        prefix=FILE_PREFIX_REPORT,
        index=index
    )


def _write_text(path: Path, content: str) -> None:
    """Write text to disk, logging and re-raising any OSError."""
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        log_and_raise(exc, f"Failed to write text file {path}")


def _write_json(path: Path, payload: dict) -> None:
    """Serialize payload and write to disk, logging and re-raising any OSError."""
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        log_and_raise(exc, f"Failed to write JSON file {path}")


def save_bug_report(session_id: str, messages: List[Dict[str, str]], conversation_id: int = None) -> Dict[str, Path]:
    bugs = detect_bugs(messages)
    paths = report_paths(conversation_id)
    payload = {
        "session_id": session_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "bug_count": len(bugs),
        "bugs": bugs,
    }

    _write_json(paths[FILE_EXT_JSON], payload)

    lines = [
        f"# Bug Report: {session_id}",
        "",
        f"Updated: {payload['updated_at']}",
        f"Bug count: {len(bugs)}",
        "",
    ]

    if not bugs:
        lines.append("No rule-based bugs detected.")
    else:
        for bug in bugs:
            lines.extend(
                [
                    f"## {bug['severity'].upper()}: {bug['id']}",
                    bug["description"],
                    "",
                    f"Evidence: {bug['evidence']}",
                    "",
                ]
            )

    _write_text(paths[FILE_EXT_MD], "\n".join(lines))
    return paths
