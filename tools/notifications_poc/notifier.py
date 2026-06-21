"""Dry-run notifier adapter for the scratch-only pilot."""

from __future__ import annotations

import importlib
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


class AppriseExerciseError(RuntimeError):
    """Raised when explicit real-Apprise exercise cannot run."""


_APPRISE_LOCAL_SCHEMA = "codexlocalpoc"
_APPRISE_CALLBACK_EVENTS: list[dict[str, Any]] = []
_APPRISE_CUSTOM_TARGET_REGISTERED = False


def _base_apprise_probe(import_available: bool) -> dict[str, Any]:
    return {
        "dependency": "apprise",
        "import_available": import_available,
        "apprise_import_available": import_available,
        "apprise_version": None,
        "behavior_exercised": False,
        "real_apprise_exercised": False,
        "apprise_delivery_mode": "not_exercised",
        "external_notification_sent": False,
        "network_delivery_attempted": False,
        "credentials_used": False,
        "github_write_performed": False,
        "dependency_files_touched": False,
        "recommendation": "conditional_adopt_candidate",
    }


def _register_apprise_local_target() -> None:
    """Register a local in-process Apprise decorator target once per process."""

    global _APPRISE_CUSTOM_TARGET_REGISTERED
    if _APPRISE_CUSTOM_TARGET_REGISTERED:
        return

    from apprise.decorators import notify

    @notify(on=_APPRISE_LOCAL_SCHEMA, name="Codex Local No-Network PoC")
    def _codex_local_notify(
        body: str,
        title: str,
        notify_type: str,
        *args: Any,
        meta: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> bool:
        _APPRISE_CALLBACK_EVENTS.append(
            {
                "body": body,
                "title": title,
                "notify_type": notify_type,
                "schema": (meta or {}).get("schema"),
                "url": (meta or {}).get("url"),
            }
        )
        return True

    _APPRISE_CUSTOM_TARGET_REGISTERED = True


def _exercise_apprise_local_no_network() -> dict[str, Any]:
    """Exercise real Apprise through a local decorator target.

    The decorator target is an in-process callback registered with Apprise. It
    does not use credentials, external service URLs, sockets, GitHub APIs, or
    desktop/OS notification channels.
    """

    apprise = importlib.import_module("apprise")
    _register_apprise_local_target()
    _APPRISE_CALLBACK_EVENTS.clear()

    app = apprise.Apprise()
    target_url = f"{_APPRISE_LOCAL_SCHEMA}://"
    target_added = bool(app.add(target_url))
    notify_result = bool(
        app.notify(
            title="WP-PILOT-NOTIFICATIONS-APPROVALS-01 local Apprise PoC",
            body="local no-network no-credential Apprise exercise",
        )
    )
    callback_count = len(_APPRISE_CALLBACK_EVENTS)
    exercised = target_added and notify_result and callback_count == 1

    return {
        "apprise_version": getattr(apprise, "__version__", "unknown"),
        "apprise_object_constructed": True,
        "apprise_target_added": target_added,
        "apprise_notify_result": notify_result,
        "apprise_callback_count": callback_count,
        "apprise_callback_schema": _APPRISE_CALLBACK_EVENTS[0]["schema"]
        if _APPRISE_CALLBACK_EVENTS
        else None,
        "apprise_callback_url": _APPRISE_CALLBACK_EVENTS[0]["url"]
        if _APPRISE_CALLBACK_EVENTS
        else None,
        "behavior_exercised": exercised,
        "real_apprise_exercised": exercised,
        "apprise_delivery_mode": "local_no_network_no_credentials"
        if exercised
        else "local_no_network_no_credentials_failed",
        "exercise_reason": (
            "Real Apprise imported, constructed an apprise.Apprise object, "
            "registered a local in-process decorator target, added its URL, "
            "and called notify without credentials or external delivery."
        ),
    }


def probe_apprise(*, exercise: bool = False) -> dict[str, Any]:
    """Return an Apprise dependency probe, optionally exercising real Apprise."""

    spec = importlib.util.find_spec("apprise")
    probe = _base_apprise_probe(import_available=spec is not None)
    if spec is None:
        probe["exercise_reason"] = (
            "Apprise is not importable in this Python environment; repo "
            "dependency files were not mutated."
        )
        if exercise:
            raise AppriseExerciseError(probe["exercise_reason"])
        return probe

    if not exercise:
        probe["apprise_version"] = getattr(
            importlib.import_module("apprise"), "__version__", "unknown"
        )
        probe["exercise_reason"] = (
            "Apprise is importable, but real behavior was not requested. "
            "Default repo mode remains local JSONL only."
        )
        return probe

    probe.update(_exercise_apprise_local_no_network())
    if not probe["real_apprise_exercised"]:
        raise AppriseExerciseError("Real Apprise local no-network exercise failed")
    return probe
