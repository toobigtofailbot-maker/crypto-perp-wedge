"""Generate denominator_manifest.json for WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01."""
import json

FUNDING_LOOKBACKS = [2880, 8640, 17280]
TAIL_PAIRS = [(0.1, 0.9), (0.05, 0.95)]
EXIT_MODES = ["fixed_max_hold_only", "midline_reversion_or_max_hold"]
MAX_HOLDS = [16, 32, 96]
RISK_STATES = ["no_atr", "atr_20", "atr_30"]


def make_variant_id(fl, lo, hi, em, hold):
    lo_str = f"{int(lo * 100):02d}"
    hi_str = f"{int(hi * 100):02d}"
    exit_short = "fixed" if em == "fixed_max_hold_only" else "midline"
    return f"fl{fl}_tail{lo_str}_{hi_str}_exit{exit_short}_hold{hold}"


rows = []
for risk_state in RISK_STATES:
    state_rows = []
    gen_order = 0
    for fl in FUNDING_LOOKBACKS:
        for lo, hi in TAIL_PAIRS:
            for em in EXIT_MODES:
                for hold in MAX_HOLDS:
                    gen_order += 1
                    vid = make_variant_id(fl, lo, hi, em, hold)
                    composite_id = f"{risk_state}:{vid}"
                    state_rows.append({
                        "composite_row_id": composite_id,
                        "risk_control_state": risk_state,
                        "variant_id": vid,
                        "generation_order_within_state": gen_order,
                        "parameter_values": {
                            "funding_lookback_bars": fl,
                            "lower_entry_percentile": lo,
                            "upper_entry_percentile": hi,
                            "exit_mode": em,
                            "max_hold_bars": hold,
                        },
                        "atr_stop_enabled": risk_state != "no_atr",
                        "atr_lookback": 14 if risk_state != "no_atr" else None,
                        "atr_multiplier": 2.0 if risk_state == "atr_20" else (3.0 if risk_state == "atr_30" else None),
                        "result_status": "not_attempted",
                    })
    assert len(state_rows) == 36, f"Expected 36 rows for {risk_state}, got {len(state_rows)}"
    rows.extend(state_rows)

assert len(rows) == 108, f"Expected 108 total rows, got {len(rows)}"

# Verify uniqueness
composite_ids = [r["composite_row_id"] for r in rows]
assert len(set(composite_ids)) == 108, "Duplicate composite IDs detected!"

manifest = {
    "package": "WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01",
    "hypothesis_id": "H-FUNDING-FADE-RISKMANAGED-01",
    "stage": "stage_1_triage_input_prep_only",
    "execution_authorized": False,
    "total_rows": 108,
    "rows_per_state": {"no_atr": 36, "atr_20": 36, "atr_30": 36},
    "composite_id_convention": "{risk_state}:{signal_variant_id}",
    "signal_axes": {
        "funding_lookback_bars": [2880, 8640, 17280],
        "entry_tail_pairs": [{"lower": 0.1, "upper": 0.9}, {"lower": 0.05, "upper": 0.95}],
        "exit_modes": ["fixed_max_hold_only", "midline_reversion_or_max_hold"],
        "max_hold_bars": [16, 32, 96],
        "formula": "3 funding lookbacks x 2 entry tail pairs x 2 exit modes x 3 max holds = 36 rows per state",
    },
    "risk_control_states": [
        {"state": "no_atr", "atr_stop_enabled": False, "atr_lookback": None, "atr_multiplier": None, "rows": 36},
        {"state": "atr_20", "atr_stop_enabled": True, "atr_lookback": 14, "atr_multiplier": 2.0, "rows": 36},
        {"state": "atr_30", "atr_stop_enabled": True, "atr_lookback": 14, "atr_multiplier": 3.0, "rows": 36},
    ],
    "winner_only_reporting_forbidden": True,
    "all_rows_must_be_reported": True,
    "rows": rows,
}

out_path = "scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/denominator_manifest.json"
with open(out_path, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"Written: {out_path} ({len(rows)} rows)")

# Spot check
print("First 3 composite IDs:", [r["composite_row_id"] for r in rows[:3]])
print("Middle 3:", [r["composite_row_id"] for r in rows[35:38]])
print("Last 3:", [r["composite_row_id"] for r in rows[-3:]])
print("State counts:", {s: sum(1 for r in rows if r["risk_control_state"] == s) for s in RISK_STATES})
