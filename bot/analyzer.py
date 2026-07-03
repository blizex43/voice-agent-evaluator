import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from enums.bug_rules import BUG_RULES
from enums.dir import REPORT_DIR
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


def report_paths() -> Dict[str, Path]:
    ensure_output_dir(REPORT_DIR)
    return get_incremented_file_dirs("report_", REPORT_DIR, {"json": "json", "md": "md"})


def save_bug_report(session_id: str, messages: List[Dict[str, str]]) -> Dict[str, Path]:
    bugs = detect_bugs(messages)
    paths = report_paths()
    payload = {
        "session_id": session_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "bug_count": len(bugs),
        "bugs": bugs,
    }

    paths["json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")

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

    paths["md"].write_text("\n".join(lines), encoding="utf-8")
    return paths
