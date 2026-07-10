"""Capture GET /api/strategies/{id} envelopes from the unchanged read-only API.

Read-only. Uses FastAPI TestClient against `tools.operator_dashboard_api.app`,
the same provenance path used for every other committed dashboard fixture.
Writes one file per committed strategy spec, verbatim, plus one `unavailable`
envelope so the frontend's not-found path renders real API shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from tools.operator_dashboard_api.app import create_app

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "operator_dashboard_frontend" / "src" / "lib" / "fixtures" / "strategies"


def main() -> None:
    client = TestClient(create_app())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    listing = client.get("/api/strategies")
    listing.raise_for_status()
    ids = [i["strategy_id"] for i in listing.json()["data"]["items"]]

    for strategy_id in ids:
        response = client.get(f"/api/strategies/{strategy_id}")
        response.raise_for_status()
        payload = response.json()
        assert payload["data"]["status"] == "available", strategy_id
        target = OUT_DIR / f"{strategy_id}.json"
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {target.relative_to(REPO_ROOT)}")

    print(f"\ncaptured {len(ids)} strategy detail envelopes")

    # Prove the unavailable branch shape without committing a fabricated file.
    missing = client.get("/api/strategies/STRAT-SPEC-DOES-NOT-EXIST")
    print("unavailable branch:", json.dumps(missing.json()["data"]))
    print("unavailable block:", json.dumps(missing.json()["unavailable"]))


if __name__ == "__main__":
    main()
