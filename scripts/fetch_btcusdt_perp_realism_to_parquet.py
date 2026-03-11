from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if REPO_ROOT.as_posix() not in sys.path:
    sys.path.insert(0, REPO_ROOT.as_posix())

from src.data_sources.binance_perp_realism import CollectionConfig, collect_and_store


DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "binance_perp_realism.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "processed"


def load_config(path: Path) -> CollectionConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CollectionConfig(
        symbol=raw.get("symbol", "BTCUSDT"),
        polls=int(raw.get("polls", 20)),
        poll_interval_seconds=float(raw.get("poll_interval_seconds", 1.0)),
        book_ticker_bucket_seconds=int(raw.get("book_ticker_bucket_seconds", 10)),
        offline_sample=bool(raw.get("offline_sample", False)),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Binance perp realism snapshots to parquet")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--offline-sample", action="store_true", help="Use deterministic offline sample data")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.offline_sample:
        cfg = CollectionConfig(
            symbol=cfg.symbol,
            polls=cfg.polls,
            poll_interval_seconds=cfg.poll_interval_seconds,
            book_ticker_bucket_seconds=cfg.book_ticker_bucket_seconds,
            offline_sample=True,
        )
    summary = collect_and_store(cfg, args.output_dir)

    print("=== BINANCE PERP REALISM EXPORT OK ===")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
