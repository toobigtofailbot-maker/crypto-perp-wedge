from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def append_event_jsonl(path: str, event: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(event), sort_keys=True) + "\n")
