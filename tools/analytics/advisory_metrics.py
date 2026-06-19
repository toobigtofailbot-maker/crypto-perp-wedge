"""Deterministic repo-native advisory analytics over chronological return data."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import pandas as pd


class AdvisoryMetricsError(ValueError):
    """Raised when analytics inputs cannot be normalized without inventing data."""


def _series(values: pd.Series | Sequence[float], *, name: str) -> pd.Series:
    series = values.copy() if isinstance(values, pd.Series) else pd.Series(values)
    if series.empty:
        raise AdvisoryMetricsError(f"{name} must contain at least one observation")
    try:
        series = series.astype(float)
    except (TypeError, ValueError) as exc:
        raise AdvisoryMetricsError(f"{name} must contain only numeric observations") from exc
    if not all(math.isfinite(float(value)) for value in series):
        raise AdvisoryMetricsError(f"{name} must contain only finite observations")
    if not series.index.is_unique:
        raise AdvisoryMetricsError(f"{name} index must be unique")
    if not series.index.is_monotonic_increasing:
        raise AdvisoryMetricsError(f"{name} index must already be chronological")
    series.name = name
    return series


def normalize_inputs(
    *,
    equity: pd.Series | Sequence[float] | None = None,
    returns: pd.Series | Sequence[float] | None = None,
) -> dict[str, pd.Series]:
    """Normalize exactly one chronological equity or simple-return series.

    Returns are never reordered or inferred from aggregate result rows. Return input is
    converted to a unit equity path with an explicit initial observation.
    """

    if (equity is None) == (returns is None):
        raise AdvisoryMetricsError("provide exactly one of equity or returns")

    if equity is not None:
        equity_series = _series(equity, name="equity")
        if (equity_series <= 0.0).any():
            raise AdvisoryMetricsError("equity observations must be greater than zero")
        return_series = equity_series.pct_change().dropna()
        return_series.name = "returns"
    else:
        return_series = _series(returns, name="returns")  # type: ignore[arg-type]
        if (return_series <= -1.0).any():
            raise AdvisoryMetricsError("simple returns must be greater than -1.0")
        compounded = (1.0 + return_series).cumprod()
        equity_series = pd.concat(
            [pd.Series([1.0], index=["__initial__"]), compounded.reset_index(drop=True)]
        )
        equity_series.index = pd.Index(
            ["__initial__", *[str(label) for label in return_series.index]], dtype="object"
        )
        equity_series.name = "equity"

    return {"equity": equity_series, "returns": return_series}


def underwater_curve(equity: pd.Series | Sequence[float]) -> pd.Series:
    """Return the equity path's drawdown from its running peak as non-positive values."""

    normalized = normalize_inputs(equity=equity)["equity"]
    underwater = normalized / normalized.cummax() - 1.0
    underwater.name = "underwater"
    return underwater


def drawdown_episodes(equity: pd.Series | Sequence[float]) -> list[dict[str, Any]]:
    """Decompose an equity path into deterministic peak-to-recovery episodes."""

    normalized = normalize_inputs(equity=equity)["equity"]
    underwater = normalized / normalized.cummax() - 1.0
    labels = list(normalized.index)
    episodes: list[dict[str, Any]] = []
    start_position: int | None = None
    peak_position: int | None = None

    for position, value in enumerate(underwater):
        if float(value) < 0.0 and start_position is None:
            start_position = position
            peak_position = position - 1
        if float(value) == 0.0 and start_position is not None:
            window = underwater.iloc[start_position:position]
            trough_label = window.idxmin()
            trough_position = labels.index(trough_label)
            episodes.append(
                {
                    "peak": str(labels[peak_position]),
                    "start": str(labels[start_position]),
                    "trough": str(trough_label),
                    "recovery": str(labels[position]),
                    "depth": float(-window.min()),
                    "duration_observations": position - start_position + 1,
                    "time_to_trough_observations": trough_position - start_position + 1,
                    "recovered": True,
                }
            )
            start_position = None
            peak_position = None

    if start_position is not None:
        window = underwater.iloc[start_position:]
        trough_label = window.idxmin()
        trough_position = labels.index(trough_label)
        episodes.append(
            {
                "peak": str(labels[peak_position]),
                "start": str(labels[start_position]),
                "trough": str(trough_label),
                "recovery": None,
                "depth": float(-window.min()),
                "duration_observations": len(normalized) - start_position,
                "time_to_trough_observations": trough_position - start_position + 1,
                "recovered": False,
            }
        )
    return episodes


def max_drawdown(equity: pd.Series | Sequence[float]) -> dict[str, Any]:
    """Return maximum drawdown and its episode, if any."""

    episodes = drawdown_episodes(equity)
    if not episodes:
        return {"value": 0.0, "episode": None}
    episode = max(episodes, key=lambda item: item["depth"])
    return {"value": episode["depth"], "episode": episode}


def rolling_metrics(
    returns: pd.Series | Sequence[float],
    *,
    window: int,
    periods_per_year: float | None = None,
) -> list[dict[str, Any]]:
    """Compute rolling compounded return, volatility, and in-window drawdown."""

    series = normalize_inputs(returns=returns)["returns"]
    if not isinstance(window, int) or window < 2:
        raise AdvisoryMetricsError("rolling window must be an integer of at least 2")
    if periods_per_year is not None and periods_per_year <= 0:
        raise AdvisoryMetricsError("periods_per_year must be greater than zero")
    if len(series) < window:
        return []

    rows: list[dict[str, Any]] = []
    for end in range(window - 1, len(series)):
        values = series.iloc[end - window + 1 : end + 1]
        window_equity = normalize_inputs(returns=values)["equity"]
        volatility = float(values.std(ddof=1))
        rows.append(
            {
                "end": str(series.index[end]),
                "window_observations": window,
                "compounded_return": float((1.0 + values).prod() - 1.0),
                "volatility": volatility,
                "annualized_volatility": (
                    None
                    if periods_per_year is None
                    else float(volatility * math.sqrt(periods_per_year))
                ),
                "max_drawdown": max_drawdown(window_equity)["value"],
            }
        )
    return rows


def calmar_style(
    equity: pd.Series | Sequence[float],
    *,
    periods_per_year: float | None,
) -> dict[str, Any]:
    """Return annualized compounded return divided by maximum drawdown."""

    normalized = normalize_inputs(equity=equity)
    if periods_per_year is None:
        return {"available": False, "value": None, "reason": "periods_per_year_unavailable"}
    if periods_per_year <= 0:
        raise AdvisoryMetricsError("periods_per_year must be greater than zero")
    observations = len(normalized["returns"])
    if observations == 0:
        return {"available": False, "value": None, "reason": "insufficient_observations"}
    drawdown = max_drawdown(normalized["equity"])["value"]
    if drawdown == 0.0:
        return {"available": False, "value": None, "reason": "zero_max_drawdown"}
    total_return = float(normalized["equity"].iloc[-1] / normalized["equity"].iloc[0] - 1.0)
    annualized_return = float(
        (1.0 + total_return) ** (float(periods_per_year) / observations) - 1.0
    )
    return {
        "available": True,
        "value": annualized_return / drawdown,
        "annualized_return": annualized_return,
        "max_drawdown": drawdown,
        "periods_per_year": float(periods_per_year),
    }


def tail_metrics(returns: pd.Series | Sequence[float]) -> dict[str, Any]:
    """Return non-parametric downside and tail summaries for observed periods."""

    series = normalize_inputs(returns=returns)["returns"]
    downside = series[series < 0.0]
    lower = float(series.quantile(0.05))
    upper = float(series.quantile(0.95))
    expected_shortfall = series[series <= lower]
    return {
        "worst_period": {"label": str(series.idxmin()), "return": float(series.min())},
        "downside_count": int(len(downside)),
        "downside_frequency": float(len(downside) / len(series)),
        "mean_downside_return": None if downside.empty else float(downside.mean()),
        "downside_deviation": (
            0.0 if downside.empty else float(math.sqrt(float((downside.pow(2)).mean())))
        ),
        "lower_quantile_05": lower,
        "expected_shortfall_05": float(expected_shortfall.mean()),
        "upper_quantile_95": upper,
        "tail_ratio": None if lower == 0.0 else float(abs(upper / lower)),
    }


def analyze_chronological_series(
    *,
    equity: pd.Series | Sequence[float] | None = None,
    returns: pd.Series | Sequence[float] | None = None,
    periods_per_year: float | None = None,
    rolling_window: int | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable advisory metric bundle from real path data."""

    normalized = normalize_inputs(equity=equity, returns=returns)
    equity_series = normalized["equity"]
    return_series = normalized["returns"]
    underwater = underwater_curve(equity_series)
    rolling = (
        []
        if rolling_window is None
        else rolling_metrics(
            return_series, window=rolling_window, periods_per_year=periods_per_year
        )
    )
    return {
        "observation_count": len(return_series),
        "total_return": float(equity_series.iloc[-1] / equity_series.iloc[0] - 1.0),
        "max_drawdown": max_drawdown(equity_series),
        "drawdown_episodes": drawdown_episodes(equity_series),
        "underwater_curve": [
            {"label": str(label), "value": float(value)}
            for label, value in underwater.items()
        ],
        "rolling_metrics": rolling,
        "calmar_style": calmar_style(equity_series, periods_per_year=periods_per_year),
        "tail_metrics": tail_metrics(return_series),
    }
