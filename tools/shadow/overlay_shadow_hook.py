"""Build zero-override overlay shadow log artifacts from committed sources."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUCKET_MAPPING_PATH = REPO_ROOT / "research" / "bucket_mappings" / "BMAP-0001.bucket_mapping.json"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_SNAPSHOT_PATH = REPO_ROOT / "tests" / "fixtures" / "context_snapshot_sample.json"
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "fmp_macro_flags.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "research" / "overlay_shadow_logs" / "OSH-0001.overlay_shadow_log.json"

PERMISSION_TO_MULTIPLIER = {"ALLOW": 1.0, "ALLOW_REDUCED": 0.5, "BLOCK": 0.0}
MULTIPLIER_TO_PERMISSION = {v: k for k, v in PERMISSION_TO_MULTIPLIER.items()}
SEVERITY_RANK = {"BLOCK": 0, "ALLOW_REDUCED": 1, "ALLOW": 2}
FAIL_OPEN_WINDOW = {
    "start_utc": "1970-01-01T00:00:00Z",
    "end_utc": "2100-01-01T00:00:00Z",
    "permission": "ALLOW",
    "size_multiplier": 1.0,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _to_utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _to_utc_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _permission_for_event(config: Mapping[str, Any], event_type: str) -> str:
    configured = str(config.get("per_event_permission", {}).get(event_type, "ALLOW")).upper()
    return configured if configured in PERMISSION_TO_MULTIPLIER else "ALLOW"


def _window_minutes(config: Mapping[str, Any], event_type: str) -> tuple[int, int]:
    per_event = config.get("per_event_window_minutes", {}).get(event_type, {})
    pre = int(per_event.get("pre", 0))
    post = int(per_event.get("post", 0))
    return max(pre, 0), max(post, 0)


def _is_context_missing(snapshot: Mapping[str, Any] | None) -> bool:
    if snapshot is None:
        return True
    events = snapshot.get("events")
    if not isinstance(events, list):
        return True
    return len(events) == 0


def _merge_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not windows:
        return []

    boundaries = sorted(
        {_to_utc_datetime(window["start_utc"]) for window in windows}
        | {_to_utc_datetime(window["end_utc"]) for window in windows}
    )
    merged: list[dict[str, Any]] = []

    for index in range(len(boundaries) - 1):
        start = boundaries[index]
        end = boundaries[index + 1]
        if end <= start:
            continue

        active = [
            window
            for window in windows
            if _to_utc_datetime(window["start_utc"]) <= start
            and _to_utc_datetime(window["end_utc"]) >= end
        ]
        if not active:
            continue

        chosen_multiplier = min(float(window["size_multiplier"]) for window in active)
        candidate = {
            "start_utc": _to_utc_iso(start),
            "end_utc": _to_utc_iso(end),
            "permission": MULTIPLIER_TO_PERMISSION[chosen_multiplier],
            "size_multiplier": chosen_multiplier,
        }
        if (
            merged
            and merged[-1]["end_utc"] == candidate["start_utc"]
            and merged[-1]["permission"] == candidate["permission"]
        ):
            merged[-1]["end_utc"] = candidate["end_utc"]
        else:
            merged.append(candidate)

    return merged


def build_external_overlay_windows(
    snapshot: Mapping[str, Any] | None,
    config: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], bool]:
    """Build the external macro-window surface without importing runtime overlay code."""

    context_missing = _is_context_missing(snapshot)
    fail_open = bool(config.get("fail_open", True))

    if context_missing:
        return ([dict(FAIL_OPEN_WINDOW)] if fail_open else []), True

    windows: list[dict[str, Any]] = []
    for event in snapshot.get("events", []):
        if not isinstance(event, Mapping):
            continue
        event_type = str(event.get("event_type", "")).upper()
        if event_type not in {"CPI", "FOMC", "NFP"}:
            continue

        event_time = _to_utc_datetime(str(event.get("event_timestamp_utc")))
        pre_minutes, post_minutes = _window_minutes(config, event_type)
        permission = _permission_for_event(config, event_type)
        windows.append(
            {
                "start_utc": _to_utc_iso(event_time - timedelta(minutes=pre_minutes)),
                "end_utc": _to_utc_iso(event_time + timedelta(minutes=post_minutes)),
                "permission": permission,
                "size_multiplier": PERMISSION_TO_MULTIPLIER[permission],
            }
        )

    windows.sort(key=lambda item: (item["start_utc"], item["end_utc"], item["permission"], item["size_multiplier"]))
    return _merge_windows(windows), False


def observe_external_overlay_bucket(
    snapshot: Mapping[str, Any] | None,
    config: Mapping[str, Any],
    evaluation_time_utc: str,
) -> dict[str, Any]:
    windows, context_missing = build_external_overlay_windows(snapshot=snapshot, config=config)
    evaluation_dt = _to_utc_datetime(evaluation_time_utc)

    active_windows = [
        window
        for window in windows
        if _to_utc_datetime(str(window["start_utc"])) <= evaluation_dt <= _to_utc_datetime(str(window["end_utc"]))
    ]

    if not active_windows:
        return {
            "observed_overlay_bucket": "ALLOW",
            "observed_overlay_size_multiplier": 1.0,
            "context_missing": context_missing,
            "reason_code": "NO_ACTIVE_WINDOW",
            "decision_id": "D-0001",
        }

    chosen = sorted(
        active_windows,
        key=lambda item: (
            SEVERITY_RANK[str(item["permission"])],
            str(item["start_utc"]),
            str(item["end_utc"]),
            str(item["permission"]),
        ),
    )[0]
    permission = str(chosen["permission"])
    reason_code = "CONTEXT_MISSING_FAIL_OPEN" if context_missing else "ACTIVE_WINDOW_MATCH"
    return {
        "observed_overlay_bucket": permission,
        "observed_overlay_size_multiplier": PERMISSION_TO_MULTIPLIER[permission],
        "context_missing": context_missing,
        "reason_code": reason_code,
        "decision_id": "D-0001",
    }


def _source_agent_output_path(agent_outputs_dir: Path, source_agent_output_id: str) -> Path:
    return agent_outputs_dir / f"{source_agent_output_id}.agent_output.json"


def build_overlay_shadow_log(
    bucket_mapping: Mapping[str, Any],
    agent_output: Mapping[str, Any],
    snapshot: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    shadow_log_id: str = "OSH-0001",
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    evaluation_time_utc = str(bucket_mapping["as_of_timestamp"])
    observation = observe_external_overlay_bucket(
        snapshot=snapshot,
        config=config,
        evaluation_time_utc=evaluation_time_utc,
    )
    observed_bucket = str(observation["observed_overlay_bucket"])
    mapped_bucket = str(bucket_mapping["mapped_bucket"])

    return {
        "overlay_shadow_log_id": shadow_log_id,
        "source_bucket_mapping_id": bucket_mapping["bucket_mapping_id"],
        "source_agent_output_id": agent_output["agent_output_id"],
        "observed_overlay_bucket": observed_bucket,
        "observed_overlay_size_multiplier": observation["observed_overlay_size_multiplier"],
        "mapped_bucket": mapped_bucket,
        "size_multiplier": bucket_mapping["size_multiplier"],
        "comparison_result": "MATCH" if observed_bucket == mapped_bucket else "MISMATCH",
        "override_applied": False,
        "fail_open_preserved": True,
        "advisory_only": True,
        "observed_at": evaluation_time_utc,
        "observation_source": {
            "source_type": "committed_macro_context_fixture",
            "snapshot_path": _repo_relative(snapshot_path),
            "config_path": _repo_relative(config_path),
            "evaluation_time_utc": evaluation_time_utc,
            "decision_id": observation["decision_id"],
            "context_missing": observation["context_missing"],
            "reason_code": observation["reason_code"],
        },
        "notes": (
            "WP-7c zero-override shadow comparison. The mapper output is advisory-only and "
            "records comparison evidence only; no lib changes, no execution influence, no "
            "OMS authority, and no risk authority are created by this artifact."
        ),
    }


def build_default_overlay_shadow_log(
    bucket_mapping_path: Path = DEFAULT_BUCKET_MAPPING_PATH,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> dict[str, Any]:
    bucket_mapping = load_json(bucket_mapping_path)
    source_agent_output_id = str(bucket_mapping["source_agent_output_id"])
    agent_output = load_json(_source_agent_output_path(agent_outputs_dir, source_agent_output_id))
    snapshot = load_json(snapshot_path)
    config = load_json(config_path)
    return build_overlay_shadow_log(
        bucket_mapping=bucket_mapping,
        agent_output=agent_output,
        snapshot=snapshot,
        config=config,
        snapshot_path=snapshot_path,
        config_path=config_path,
    )


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket-mapping", type=Path, default=DEFAULT_BUCKET_MAPPING_PATH)
    parser.add_argument("--agent-outputs-dir", type=Path, default=DEFAULT_AGENT_OUTPUTS_DIR)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    payload = build_default_overlay_shadow_log(
        bucket_mapping_path=args.bucket_mapping,
        agent_outputs_dir=args.agent_outputs_dir,
        snapshot_path=args.snapshot,
        config_path=args.config,
    )

    if args.out is not None:
        write_json(args.out, payload)
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
