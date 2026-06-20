"""Dry-run notifier adapter for the scratch-only pilot."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


class LocalLogNotifier:
    """One-way dry-run notifier that writes JSONL instead of sending messages."""

    channel_kind = "local_jsonl_noop"

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path

    def notify(self, event: dict[str, Any]) -> None:
        if event.get("dry_run") is not True:
            raise ValueError("LocalLogNotifier only accepts dry_run events")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def probe_apprise() -> dict[str, Any]:
    """Return an import-only Apprise dependency probe.

    The pilot intentionally does not exercise real Apprise delivery because no
    package-scoped local/no-op Apprise URL is committed in repo truth.
    """

    spec = importlib.util.find_spec("apprise")
    return {
        "dependency": "apprise",
        "import_available": spec is not None,
        "behavior_exercised": False,
        "exercise_reason": (
            "No package-scoped local/no-op Apprise URL is configured; real outbound "
            "notification credentials and URLs are forbidden for this WP."
        ),
    }
