import json
import hashlib
import subprocess
from pathlib import Path
import pandas as pd

from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact

CFG_PATH = Path("configs") / "backtest_single_trade.json"
DATA_DIR = Path("data") / "processed"
REPORTS_DIR = Path("reports")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc(ts: str) -> pd.Timestamp:
    t = pd.Timestamp(ts)
    return t.tz_convert("UTC") if t.tzinfo else pd.Timestamp(ts, tz="UTC")


def newest_match(glob_pattern: str) -> Path:
    matches = list(DATA_DIR.glob(glob_pattern))
    if not matches:
        raise FileNotFoundError(f"No files match: {DATA_DIR}/{glob_pattern}")
    return max(matches, key=lambda p: p.stat().st_mtime)


def select_dataset(spec: dict) -> Path:
    mode = spec.get("mode")
    if mode == "latest_glob":
        return newest_match(spec["glob"])
    if mode == "path":
        return Path(spec["path"])
    raise ValueError(f"Unsupported dataset mode: {mode}")


def git_commit_id() -> str:
    # Prefer git if available
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        # Fallback: attempt to read .git/HEAD
        head = Path(".git") / "HEAD"
        if not head.exists():
            return "UNKNOWN_GIT_COMMIT"
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref: "):
            ref_path = Path(".git") / ref.replace("ref: ", "").strip()
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()
        return ref  # detached HEAD case


def main():
    # --- load config ---
    cfg_bytes = CFG_PATH.read_bytes()
    cfg_hash = sha256_bytes(cfg_bytes)
    cfg = json.loads(cfg_bytes.decode("utf-8"))

    decision_id = cfg.get("decision_id", "UNKNOWN_DECISION_ID")
    timeframe = cfg.get("timeframe")

    # --- dataset selection (from config rules) ---
    klines_path = select_dataset(cfg["datasets"]["klines"])
    funding_path = select_dataset(cfg["datasets"]["funding"])

    # --- dataset hashes (runtime truth) ---
    dataset_hashes = {
        "klines_parquet": {"path": klines_path.as_posix(), "sha256": sha256_file(klines_path)},
        "funding_parquet": {"path": funding_path.as_posix(), "sha256": sha256_file(funding_path)},
    }

    # --- parameters ---
    qty = float(cfg["trade"]["qty_base"])
    entry_t = utc(cfg["trade"]["entry_ts_utc"])
    exit_t = utc(cfg["trade"]["exit_ts_utc"])

    fee_rate = float(cfg["costs"]["fee_rate"])
    slippage_bps = float(cfg["costs"]["slippage_bps"])
    slip_frac = slippage_bps / 10_000.0

    # --- load data ---
    k = pd.read_parquet(klines_path)
    f = pd.read_parquet(funding_path)

    k["open_time"] = pd.to_datetime(k["open_time_ms"], unit="ms", utc=True)
    k["close_time"] = pd.to_datetime(k["close_time_ms"], unit="ms", utc=True)
    k = k.sort_values("open_time").reset_index(drop=True)

    f["funding_time"] = pd.to_datetime(f["fundingTime"], unit="ms", utc=True)
    f["fundingRate"] = pd.to_numeric(f["fundingRate"], errors="coerce")
    f = f.sort_values("funding_time").reset_index(drop=True)

    # --- basic timeframe sanity (minimal) ---
    if timeframe != "1h":
        raise ValueError(f"Config timeframe={timeframe} not supported by this runner (expected 1h).")

    # --- select entry/exit bars ---
    entry_row = k[k["open_time"] >= entry_t].iloc[0]
    exit_row = k[k["open_time"] >= exit_t].iloc[0]

    entry_mid = float(entry_row["open"])
    exit_mid = float(exit_row["open"])

    # --- simulate execution with adverse slippage ---
    entry_exec = entry_mid * (1.0 + slip_frac) if qty > 0 else entry_mid * (1.0 - slip_frac)
    exit_exec = exit_mid * (1.0 - slip_frac) if qty > 0 else exit_mid * (1.0 + slip_frac)

    entry_fee = fee_pnl_impact(qty, entry_exec, fee_rate)
    entry_slip = slippage_pnl_impact(qty, entry_mid, entry_exec)

    exit_fee = fee_pnl_impact(-qty, exit_exec, fee_rate)
    exit_slip = slippage_pnl_impact(-qty, exit_mid, exit_exec)

    # --- funding during hold (cashflow at event timestamps) ---
    k_close = k[["close_time", "close"]].sort_values("close_time").reset_index(drop=True)
    close_times = k_close["close_time"].values
    closes = k_close["close"].values

    held_funding = f[(f["funding_time"] >= entry_t) & (f["funding_time"] < exit_t)].copy()

    funding_pnl = 0.0
    for _, r in held_funding.iterrows():
        ft = r["funding_time"].to_datetime64()
        fr = float(r["fundingRate"]) if pd.notna(r["fundingRate"]) else 0.0
        idx = close_times.searchsorted(ft, side="right") - 1
        if idx < 0:
            continue
        mark = float(closes[idx])
        funding_pnl += funding_pnl_impact(qty, mark, fr)

    total = entry_fee + entry_slip + exit_fee + exit_slip + funding_pnl

    # --- report artifact ---
    REPORTS_DIR.mkdir(exist_ok=True)

    run_ts = pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    report = {
        "run_timestamp_utc": run_ts,
        "git_commit_id": git_commit_id(),
        "decision_id": decision_id,
        "config_path": CFG_PATH.as_posix(),
        "config_sha256": cfg_hash,
        "dataset_hashes": dataset_hashes,
        "inputs": {
            "timeframe": timeframe,
            "qty_base": qty,
            "entry_ts_utc": str(entry_t),
            "exit_ts_utc": str(exit_t),
            "fee_rate": fee_rate,
            "slippage_bps": slippage_bps,
        },
        "results": {
            "entry_bar_open_time": str(entry_row["open_time"]),
            "exit_bar_open_time": str(exit_row["open_time"]),
            "entry_mid": entry_mid,
            "entry_exec": entry_exec,
            "exit_mid": exit_mid,
            "exit_exec": exit_exec,
            "entry_fee": entry_fee,
            "entry_slippage": entry_slip,
            "exit_fee": exit_fee,
            "exit_slippage": exit_slip,
            "funding_events_held": int(len(held_funding)),
            "funding_pnl": funding_pnl,
            "total_pnl_impact": total,
        },
    }

    out_path = REPORTS_DIR / f"single_trade_report_{run_ts}.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== SINGLE TRADE RUN (CONFIG-WIRED) ===")
    print("report_path:", out_path.as_posix())
    print("config_sha256:", cfg_hash)
    print("klines_sha256:", dataset_hashes["klines_parquet"]["sha256"])
    print("funding_sha256:", dataset_hashes["funding_parquet"]["sha256"])
    print("total_pnl_impact:", total)


if __name__ == "__main__":
    main()