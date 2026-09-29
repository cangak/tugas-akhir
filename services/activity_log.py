"""Persistent, low-noise operational activity log for the application."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = PROJECT_ROOT / "data" / "audit_logs" / "activity_log.jsonl"
APP_TIMEZONE = ZoneInfo("Asia/Jakarta")
_WRITE_LOCK = threading.Lock()


def activity_log_path() -> Path:
    configured = os.environ.get("ACTIVITY_LOG_PATH", "").strip()
    return Path(configured) if configured else DEFAULT_LOG_PATH


def load_system_activities(limit: int = 20) -> list[dict[str, Any]]:
    path = activity_log_path()
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except (json.JSONDecodeError, TypeError):
                    continue
                if all(event.get(key) for key in ("timestamp", "event_type", "title")):
                    events.append(event)
    except OSError:
        return []
    events.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)
    return events[: max(0, int(limit))]


def log_system_activity(event_type: str, title: str, description: str = "",
                        metadata: dict[str, Any] | None = None, *, module: str = "",
                        dedupe_key: str | None = None) -> bool:
    """Append one real event; a stable dedupe key makes reruns idempotent."""
    event: dict[str, Any] = {
        "timestamp": datetime.now(APP_TIMEZONE).isoformat(timespec="seconds"),
        "event_type": str(event_type).strip(), "title": str(title).strip(),
        "description": str(description).strip(),
    }
    if module:
        event["module"] = module
    if metadata:
        event["metadata"] = metadata
    if dedupe_key:
        event["dedupe_key"] = str(dedupe_key)
    if not event["event_type"] or not event["title"]:
        raise ValueError("event_type dan title wajib diisi")
    path = activity_log_path()
    with _WRITE_LOCK:
        if dedupe_key and any(item.get("dedupe_key") == dedupe_key for item in load_system_activities(5000)):
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
    return True
