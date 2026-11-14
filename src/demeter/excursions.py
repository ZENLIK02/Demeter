"""The science core: pure functions, no I/O. Easy to unit-test and to explain to judges.

For one site and one variable:
  1. baseline threshold per calendar month = max(q-quantile, median + min_delta) of the
     baseline years (mirrored for direction == "lower").
  2. a month is an EXCURSION when its value is past that threshold in the non-Mars direction.
  3. rate = excursion months per year, for the baseline and the recent period.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MIN_BASELINE_YEARS = 5  # per calendar month; fewer -> no threshold (e.g. SMAP starts 2015)


@dataclass
class VariableResult:
    variable: str
    source: str
    dates: list[str]
    values: list[float]
    threshold: list[float | None]
    excursion: list[bool]
    excursions_per_year: dict[str, int]
    rate_baseline: float | None
    rate_recent: float | None
    change: float | None
    drifting: bool
    note: str = ""
    extra: dict = field(default_factory=dict)


def to_series(df: pd.DataFrame) -> pd.Series:
    """Long raw rows for ONE variable -> monthly Series indexed by Period[M]."""
    s = pd.Series(df["value"].to_numpy(dtype=float), index=pd.PeriodIndex(df["date"], freq="M"))
    return s.sort_index()


def monthly_thresholds(
    s: pd.Series, baseline: tuple[int, int], quantile: float, min_delta: float, direction: str
) -> dict[int, float]:
    base = s[(s.index.year >= baseline[0]) & (s.index.year <= baseline[1])]
    out: dict[int, float] = {}
    for month in range(1, 13):
        vals = base[base.index.month == month].dropna().to_numpy()
        if len(vals) < MIN_BASELINE_YEARS:
            continue
        median = float(np.median(vals))
        if direction == "higher":
            out[month] = max(float(np.quantile(vals, quantile)), median + min_delta)
        else:
            out[month] = min(float(np.quantile(vals, 1 - quantile)), median - min_delta)
    return out


def flag_excursions(s: pd.Series, thresholds: dict[int, float], direction: str) -> pd.Series:
    thr = pd.Series([thresholds.get(m) for m in s.index.month], index=s.index, dtype=float)
    flags = s > thr if direction == "higher" else s < thr
    return flags.fillna(False).astype(bool)


def rate_per_year(flags: pd.Series, period: tuple[int, int], valid: pd.Series) -> float | None:
    """Excursion months per year in `period`, counting only months that have a threshold."""
    in_period = (flags.index.year >= period[0]) & (flags.index.year <= period[1]) & valid.to_numpy()
    n_months = int(in_period.sum())
    if n_months < 24:  # need at least two years of usable months
        return None
    return float(flags[in_period].sum()) / (n_months / 12.0)


def analyze_variable(
    df: pd.DataFrame,
    *,
    variable: str,
    source: str,
    baseline: tuple[int, int],
    recent: tuple[int, int],
    quantile: float,
    min_delta: float,
    direction: str,
    drift_change: float,
) -> VariableResult:
    s = to_series(df)
    thresholds = monthly_thresholds(s, baseline, quantile, min_delta, direction)
    flags = flag_excursions(s, thresholds, direction)
    valid = pd.Series([m in thresholds for m in s.index.month], index=s.index)

    rate_b = rate_per_year(flags, baseline, valid)
    rate_r = rate_per_year(flags, recent, valid)
    change = None if rate_b is None or rate_r is None else rate_r - rate_b
    note = ""
    if not thresholds:
        note = f"no {baseline[0]}-{baseline[1]} baseline (data starts {s.index.min()})"
    elif rate_r is None:
        note = f"not enough data in {recent[0]}-{recent[1]}"

    per_year = flags.groupby(flags.index.year).sum()
    return VariableResult(
        variable=variable,
        source=source,
        dates=[str(p) for p in s.index],
        values=[round(float(v), 4) for v in s.to_numpy()],
        threshold=[None if m not in thresholds else round(thresholds[m], 4) for m in s.index.month],
        excursion=[bool(x) for x in flags.to_numpy()],
        excursions_per_year={str(y): int(n) for y, n in per_year.items()},
        rate_baseline=None if rate_b is None else round(rate_b, 3),
        rate_recent=None if rate_r is None else round(rate_r, 3),
        change=None if change is None else round(change, 3),
        drifting=bool(change is not None and change >= drift_change),
        note=note,
    )
