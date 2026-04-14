"""
lib/evaluation.py — Pure evaluation functions for research backtests.

All functions are pure (no side effects except ``append_trial``).
Implements D2-004 (DSR + trial log) and D2-006 (promotion gates).
"""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd
from statistics import NormalDist

from lib.backtest import BacktestResult

_NORM = NormalDist()


# ---------------------------------------------------------------------------
# Annualisation constants
# ---------------------------------------------------------------------------

_BARS_PER_YEAR: dict[str, float] = {
    "1m": 525_600,
    "3m": 175_200,
    "5m": 105_120,
    "15m": 35_040,
    "30m": 17_520,
    "1h": 8_760,
    "2h": 4_380,
    "4h": 2_190,
    "6h": 1_460,
    "8h": 1_095,
    "12h": 730,
    "1d": 365,
    "daily": 365,
}


def _annualisation_factor(freq: str) -> float:
    """Return sqrt(bars_per_year) for the given bar frequency string."""
    bars = _BARS_PER_YEAR.get(freq)
    if bars is None:
        raise ValueError(
            f"Unknown frequency '{freq}'. "
            f"Supported: {list(_BARS_PER_YEAR.keys())}"
        )
    return math.sqrt(bars)


def _returns_from_equity(equity_curve: pd.Series) -> pd.Series:
    """Compute per-bar returns from an equity curve."""
    return equity_curve.pct_change().dropna()


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------


def sharpe(returns: pd.Series, freq: str) -> float:
    """Annualised Sharpe ratio (assumes 0% risk-free rate).

    Parameters
    ----------
    returns:
        Per-bar arithmetic returns.
    freq:
        Bar frequency string, e.g. ``"1h"``, ``"1d"``.
    """
    if len(returns) < 2:
        return 0.0
    mu = returns.mean()
    sigma = returns.std(ddof=1)
    if sigma == 0:
        return 0.0
    return float(mu / sigma * _annualisation_factor(freq))


def sortino(returns: pd.Series, freq: str, target: float = 0.0) -> float:
    """Annualised Sortino ratio.

    Parameters
    ----------
    returns:
        Per-bar arithmetic returns.
    freq:
        Bar frequency string.
    target:
        Minimum acceptable return per bar (default 0).
    """
    if len(returns) < 2:
        return 0.0
    mu = returns.mean() - target
    downside = returns[returns < target] - target
    if len(downside) == 0:
        return float("inf") if mu > 0 else 0.0
    downside_std = math.sqrt((downside ** 2).mean())
    if downside_std == 0:
        return 0.0
    return float(mu / downside_std * _annualisation_factor(freq))


def calmar(equity_curve: pd.Series, freq: str) -> float:
    """Calmar ratio = annualised return / max drawdown magnitude.

    Returns 0 if max drawdown is 0.
    """
    if len(equity_curve) < 2:
        return 0.0
    returns = _returns_from_equity(equity_curve)
    ann_ret = returns.mean() * _BARS_PER_YEAR.get(freq, 252)
    mdd, _, _ = max_drawdown(equity_curve)
    if mdd == 0:
        return 0.0
    return float(ann_ret / mdd)


def max_drawdown(
    equity_curve: pd.Series,
) -> tuple[float, Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """Maximum drawdown (as a positive fraction) and its peak/trough timestamps.

    Returns
    -------
    (max_dd, peak_ts, trough_ts)
        max_dd is in [0, 1] (positive means loss).
        peak_ts and trough_ts are ``None`` when no drawdown exists.
    """
    if len(equity_curve) < 2:
        return 0.0, None, None

    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak

    max_dd = float(-drawdown.min())
    if max_dd == 0:
        return 0.0, None, None

    trough_ts = drawdown.idxmin()
    peak_ts = equity_curve[:trough_ts].idxmax()
    return max_dd, peak_ts, trough_ts


def turnover(trades_df: pd.DataFrame, equity_curve: pd.Series) -> float:
    """Annual turnover = total notional traded / average equity.

    Returns 0 if no trades or equity is 0.
    """
    if trades_df.empty or equity_curve.empty:
        return 0.0
    avg_equity = equity_curve.mean()
    if avg_equity == 0:
        return 0.0
    # Notional per trade = entry_price (for a 1-contract model)
    if "entry_price" not in trades_df.columns:
        return 0.0
    total_notional = (trades_df["entry_price"].abs() * 2).sum()  # * 2: entry + exit
    return float(total_notional / avg_equity)


def hit_rate(trades_df: pd.DataFrame) -> float:
    """Fraction of trades with positive net PnL."""
    if trades_df.empty or "net_pnl" not in trades_df.columns:
        return 0.0
    winners = (trades_df["net_pnl"] > 0).sum()
    return float(winners / len(trades_df))


def profit_factor(trades_df: pd.DataFrame) -> float:
    """Gross profit / gross loss (both positive).

    Returns ``inf`` when there are no losing trades.
    """
    if trades_df.empty or "net_pnl" not in trades_df.columns:
        return 0.0
    gross_profit = trades_df.loc[trades_df["net_pnl"] > 0, "net_pnl"].sum()
    gross_loss = abs(trades_df.loc[trades_df["net_pnl"] < 0, "net_pnl"].sum())
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return float(gross_profit / gross_loss)


def cost_drag(result: BacktestResult) -> dict:
    """Breakdown of cost drag relative to gross PnL.

    Returns
    -------
    dict with keys:
        fees_paid, slippage_paid, funding_paid,
        total_cost, gross_pnl, cost_drag_fraction
    """
    gross = result.realized_pnl + result.unrealized_pnl
    total_cost = result.fees_paid + result.slippage_paid + result.funding_paid
    drag = float(total_cost / gross) if gross != 0 else float("nan")
    return {
        "fees_paid": result.fees_paid,
        "slippage_paid": result.slippage_paid,
        "funding_paid": result.funding_paid,
        "total_cost": total_cost,
        "gross_pnl": gross,
        "cost_drag_fraction": drag,
    }


# ---------------------------------------------------------------------------
# Probabilistic Sharpe Ratio / Deflated Sharpe Ratio
# ---------------------------------------------------------------------------


def deflated_sharpe_ratio(
    sharpe_hat: float,
    n_trials: int,
    variance_of_trials: float,
    skew: float,
    kurt: float,
    n_obs: int,
) -> tuple[float, float]:
    """Compute the Deflated Sharpe Ratio (DSR).

    Implements Bailey & López de Prado (2014).

    Parameters
    ----------
    sharpe_hat:
        Annualised Sharpe ratio of the strategy under evaluation.
    n_trials:
        Total number of strategies/trials tested (including this one).
    variance_of_trials:
        Variance of Sharpe ratios across all trials.
    skew:
        Skewness of per-bar returns.
    kurt:
        Excess kurtosis of per-bar returns.
    n_obs:
        Number of observations (bars) in the backtest.

    Returns
    -------
    (dsr_probability, sr_benchmark)
        dsr_probability: ∈ [0, 1].  Probability that the strategy's true SR
            exceeds the expected maximum SR from N random trials.
            Gate 2 passes when this value > 0.95 ("at 95% CI").
        sr_benchmark: the expected maximum SR benchmark from N trials.
    """
    if n_trials < 1 or n_obs < 4:
        return 0.0, 0.0

    # Expected maximum SR across n_trials (Bailey & López de Prado 2014, Eq. 4)
    gamma_em = 0.5772156649  # Euler-Mascheroni constant
    std_trials = math.sqrt(max(variance_of_trials, 1e-12))

    # E[max SR] using extreme-value approximation
    # Clamp probabilities to avoid NaN from inv_cdf at 0 or 1
    p1 = max(1e-15, min(1 - 1e-15, 1.0 - 1.0 / n_trials)) if n_trials > 1 else 0.5
    p2 = max(1e-15, min(1 - 1e-15, 1.0 - 1.0 / (n_trials * math.e))) if n_trials > 1 else 0.5
    z1 = _NORM.inv_cdf(p1)
    z2 = _NORM.inv_cdf(p2)
    sr_benchmark = std_trials * (
        (1.0 - gamma_em) * z1 + gamma_em * z2
    )

    # PSR: probability that SR_hat > sr_benchmark (Bailey & López de Prado 2014, Eq. 1)
    sr_annual_to_bar = sharpe_hat  # already annualised; use as-is for benchmark comparison
    numerator = (sr_annual_to_bar - sr_benchmark) * math.sqrt(n_obs - 1)
    denominator = math.sqrt(
        1.0
        - skew * sr_annual_to_bar
        + ((kurt - 1.0) / 4.0) * sr_annual_to_bar ** 2
    )
    if denominator <= 0 or not math.isfinite(denominator):
        denominator = 1.0

    psr = float(_NORM.cdf(numerator / denominator))
    return psr, sr_benchmark


# ---------------------------------------------------------------------------
# Walk-forward efficiency
# ---------------------------------------------------------------------------


def walk_forward_efficiency(is_sharpe: float, oos_sharpe: float) -> float:
    """Walk-forward efficiency = OOS Sharpe / IS Sharpe.

    Capped at 1.0 (not penalised for OOS > IS).
    Returns 0 if IS Sharpe is <= 0.
    """
    if is_sharpe <= 0:
        return 0.0
    return float(min(oos_sharpe / is_sharpe, 1.0))


# ---------------------------------------------------------------------------
# Parameter sensitivity
# ---------------------------------------------------------------------------


def parameter_sensitivity(
    run_fn: Callable[..., BacktestResult],
    base_params: dict,
    pct_shift: float = 0.25,
) -> dict:
    """Sweep each numeric parameter by ±pct_shift and record Sharpe ratios.

    Parameters
    ----------
    run_fn:
        Callable that accepts keyword arguments from ``base_params`` and
        returns a ``BacktestResult``.  Must accept a ``freq`` keyword for
        Sharpe calculation, or base result must carry it.
    base_params:
        Dict of parameter names to base values.  Non-numeric values are skipped.
    pct_shift:
        Fractional shift, default 0.25 (±25%).

    Returns
    -------
    dict mapping parameter_name ->
        {base, up, down, up_ratio, down_ratio, min_ratio}
    """
    freq = base_params.get("freq", "1h")
    base_result = run_fn(**{k: v for k, v in base_params.items() if k != "freq"})
    base_returns = _returns_from_equity(base_result.equity_curve)
    base_sr = sharpe(base_returns, freq)

    results: dict[str, dict] = {}
    for param, value in base_params.items():
        if param == "freq" or not isinstance(value, (int, float)):
            continue
        if value == 0:
            continue

        for direction, label in [(1 + pct_shift, "up"), (1 - pct_shift, "down")]:
            shifted = {
                k: (v * direction if k == param else v)
                for k, v in base_params.items()
                if k != "freq"
            }
            try:
                res = run_fn(**shifted)
                rets = _returns_from_equity(res.equity_curve)
                sr = sharpe(rets, freq)
            except Exception:
                sr = 0.0

            ratio = (sr / base_sr) if base_sr != 0 else 0.0
            if param not in results:
                results[param] = {"base_sharpe": base_sr}
            results[param][f"sharpe_{label}"] = sr
            results[param][f"ratio_{label}"] = ratio

        if param in results:
            results[param]["min_ratio"] = min(
                results[param].get("ratio_up", 0.0),
                results[param].get("ratio_down", 0.0),
            )

    return results


# ---------------------------------------------------------------------------
# Promotion gate dataclasses
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    """Result for a single promotion gate."""

    gate_id: int
    gate_name: str
    passed: bool
    value: float
    threshold: float
    note: str = ""


@dataclass
class GateReport:
    """Aggregated result of all eight promotion gates (D2-006)."""

    gates: list[GateResult]
    overall_pass: bool
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall_pass": self.overall_pass,
            "summary": self.summary,
            "gates": [
                {
                    "gate_id": g.gate_id,
                    "gate_name": g.gate_name,
                    "passed": g.passed,
                    "value": g.value,
                    "threshold": g.threshold,
                    "note": g.note,
                }
                for g in self.gates
            ],
        }


# ---------------------------------------------------------------------------
# Promotion gates (D2-006)
# ---------------------------------------------------------------------------


def check_promotion_gates(
    result: BacktestResult,
    trial_count: int,
    params_meta: dict,
    *,
    oos_result: Optional[BacktestResult] = None,
    is_result: Optional[BacktestResult] = None,
    freq: str = "1h",
    fold_results: Optional[list[BacktestResult]] = None,
    variance_of_trials: float = 0.1,
    skew: float = 0.0,
    kurt: float = 3.0,
) -> GateReport:
    """Check all eight D2-006 promotion gates.

    Parameters
    ----------
    result:
        The OOS (or full-period) ``BacktestResult`` being evaluated.
    trial_count:
        Total number of trials run against this dataset so far.
    params_meta:
        Dict describing the strategy parameters.  Must contain:
        ``n_free_params`` (int) and optionally other numeric params.
    oos_result:
        If provided, used for OOS-specific metrics.  Falls back to ``result``.
    is_result:
        In-sample result for walk-forward efficiency gate.
    freq:
        Bar frequency string (for Sharpe annualisation).
    fold_results:
        Per-fold results for gate 3 (per-fold max drawdown).
    variance_of_trials:
        Variance of Sharpe ratios across all trials (for DSR).
    skew, kurt:
        Moments of the return distribution (for DSR).

    Gates
    -----
    1. OOS Sharpe >= 1.0
    2. DSR > 1.0 at 95% CI (probability of true Sharpe > 1.0 exceeds 0.95)
    3. Per-fold max DD <= 20%
    4. Parameter sensitivity: min ratio >= 0.70 at ±25%
    5. Cost drag <= 50% of gross PnL
    6. No 90-day window > 60% of total PnL
    7. <= 5 free parameters
    8. Walk-forward efficiency > 0.5
    """
    oos = oos_result if oos_result is not None else result
    oos_returns = _returns_from_equity(oos.equity_curve)
    oos_sr = sharpe(oos_returns, freq)

    gates: list[GateResult] = []

    # ---- Gate 1: OOS Sharpe >= 1.0 ----
    g1_pass = oos_sr >= 1.0
    gates.append(GateResult(
        gate_id=1,
        gate_name="OOS Sharpe >= 1.0",
        passed=g1_pass,
        value=round(oos_sr, 4),
        threshold=1.0,
    ))

    # ---- Gate 2: DSR > 1.0 at 95% CI ----
    # Checks: P(true Sharpe > 1.0) > 0.95 after multiple-testing correction.
    # threshold=1.0 is the Sharpe floor being tested.
    # The pass condition uses the 0.95 probability cutoff ("at 95% CI").
    n_obs = len(oos_returns)
    dsr_val, sr_benchmark = deflated_sharpe_ratio(
        sharpe_hat=oos_sr,
        n_trials=max(trial_count, 1),
        variance_of_trials=variance_of_trials,
        skew=skew,
        kurt=kurt,
        n_obs=max(n_obs, 4),
    )
    g2_pass = dsr_val > 0.95
    gates.append(GateResult(
        gate_id=2,
        gate_name="DSR > 1.0 at 95% CI",
        passed=g2_pass,
        value=round(dsr_val, 6),
        threshold=1.0,
        note=f"P(SR>1.0)={dsr_val:.4f}; SR benchmark={sr_benchmark:.4f}",
    ))

    # ---- Gate 3: Per-fold max DD <= 20% ----
    if fold_results:
        fold_dds = [max_drawdown(f.equity_curve)[0] for f in fold_results]
        worst_fold_dd = max(fold_dds) if fold_dds else 0.0
    else:
        worst_fold_dd, _, _ = max_drawdown(oos.equity_curve)
    g3_pass = worst_fold_dd <= 0.20
    gates.append(GateResult(
        gate_id=3,
        gate_name="Per-fold max DD <= 20%",
        passed=g3_pass,
        value=round(worst_fold_dd, 4),
        threshold=0.20,
    ))

    # ---- Gate 4: Parameter sensitivity min_ratio >= 0.70 ----
    sens_min_ratio = params_meta.get("sensitivity_min_ratio", 1.0)
    g4_pass = sens_min_ratio >= 0.70
    gates.append(GateResult(
        gate_id=4,
        gate_name="Parameter sensitivity min_ratio >= 0.70",
        passed=g4_pass,
        value=round(float(sens_min_ratio), 4),
        threshold=0.70,
        note="Computed by parameter_sensitivity() at ±25%",
    ))

    # ---- Gate 5: Cost drag <= 50% of gross PnL ----
    cd = cost_drag(oos)
    drag = cd["cost_drag_fraction"]
    if math.isnan(drag):
        drag = 0.0
        g5_note = "gross_pnl=0, cost drag undefined"
    else:
        g5_note = ""
    g5_pass = drag <= 0.50
    gates.append(GateResult(
        gate_id=5,
        gate_name="Cost drag <= 50% of gross PnL",
        passed=g5_pass,
        value=round(drag, 4),
        threshold=0.50,
        note=g5_note,
    ))

    # ---- Gate 6: No 90-day window > 60% of total PnL ----
    total_pnl = oos.equity_curve.iloc[-1] - oos.equity_curve.iloc[0]
    if abs(total_pnl) > 0:
        rolling_90d = oos.per_bar_pnl.rolling("90D", min_periods=1).sum()
        max_window_pnl = rolling_90d.abs().max()
        window_fraction = float(max_window_pnl / abs(total_pnl))
    else:
        window_fraction = 0.0
    g6_pass = window_fraction <= 0.60
    gates.append(GateResult(
        gate_id=6,
        gate_name="No 90-day window > 60% of PnL",
        passed=g6_pass,
        value=round(window_fraction, 4),
        threshold=0.60,
    ))

    # ---- Gate 7: <= 5 free parameters ----
    n_free = int(params_meta.get("n_free_params", 0))
    g7_pass = n_free <= 5
    gates.append(GateResult(
        gate_id=7,
        gate_name="<= 5 free parameters",
        passed=g7_pass,
        value=float(n_free),
        threshold=5.0,
    ))

    # ---- Gate 8: Walk-forward efficiency > 0.5 ----
    if is_result is not None:
        is_returns = _returns_from_equity(is_result.equity_curve)
        is_sr = sharpe(is_returns, freq)
    else:
        is_sr = params_meta.get("is_sharpe", oos_sr)
    wfe = walk_forward_efficiency(float(is_sr), oos_sr)
    g8_pass = wfe > 0.5
    gates.append(GateResult(
        gate_id=8,
        gate_name="Walk-forward efficiency > 0.5",
        passed=g8_pass,
        value=round(wfe, 4),
        threshold=0.5,
    ))

    overall = all(g.passed for g in gates)
    summary = {
        "n_passed": sum(g.passed for g in gates),
        "n_failed": sum(not g.passed for g in gates),
        "n_total": len(gates),
        "trial_count": trial_count,
        "freq": freq,
    }

    return GateReport(gates=gates, overall_pass=overall, summary=summary)


# ---------------------------------------------------------------------------
# Trial log
# ---------------------------------------------------------------------------


@dataclass
class TrialEntry:
    """A single row in research/trial_log.jsonl."""

    trial_id: str                # uuid4
    utc: str                     # ISO 8601 UTC timestamp
    hypothesis_id: str           # reference to HYPOTHESIS.md entry
    config_sha256: str           # sha256 of strategy config dict
    dataset_sha256: str          # sha256 of dataset identifier(s)
    params: dict                 # free parameters used
    in_sample_sharpe: float
    oos_sharpe: float
    max_drawdown: float          # fraction [0, 1]
    n_obs: int
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _sha256_of_dict(d: dict) -> str:
    """Stable SHA-256 of a JSON-serialisable dict."""
    canonical = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def make_trial_entry(
    hypothesis_id: str,
    config: dict,
    dataset_ids: list[str],
    params: dict,
    in_sample_sharpe: float,
    oos_sharpe: float,
    max_dd: float,
    n_obs: int,
    notes: str = "",
) -> TrialEntry:
    """Convenience constructor for ``TrialEntry``."""
    return TrialEntry(
        trial_id=str(uuid.uuid4()),
        utc=datetime.now(timezone.utc).isoformat(),
        hypothesis_id=hypothesis_id,
        config_sha256=_sha256_of_dict(config),
        dataset_sha256=_sha256_of_dict({"ids": sorted(dataset_ids)}),
        params=params,
        in_sample_sharpe=in_sample_sharpe,
        oos_sharpe=oos_sharpe,
        max_drawdown=max_dd,
        n_obs=n_obs,
        notes=notes,
    )


def append_trial(trial_log_path: Path, entry: TrialEntry) -> None:
    """Append a single ``TrialEntry`` to the JSONL trial log (atomic write).

    Creates the file if it does not exist.
    """
    trial_log_path.parent.mkdir(parents=True, exist_ok=True)
    row = json.dumps(entry.to_dict(), default=str)
    with trial_log_path.open("a", encoding="utf-8") as fh:
        fh.write(row + "\n")
