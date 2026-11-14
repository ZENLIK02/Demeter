import pandas as pd
import pytest

from demeter.excursions import analyze_variable, flag_excursions, monthly_thresholds, to_series


def make(values_by_year: dict[int, float], month_values=None):
    rows = []
    for year, v in values_by_year.items():
        for m in range(1, 13):
            rows.append({"date": f"{year}-{m:02d}", "variable": "precip", "value": v if month_values is None else month_values(year, m)})
    return pd.DataFrame(rows)


KW = dict(variable="precip", source="test", baseline=(2001, 2010), recent=(2016, 2025), quantile=0.9, direction="higher", drift_change=0.5)


def test_flat_series_has_no_excursions():
    df = make({y: 1.0 for y in range(2001, 2026)})
    r = analyze_variable(df, min_delta=0.1, **KW)
    assert r.rate_baseline == 0 and r.rate_recent == 0 and not r.drifting


def test_min_delta_stops_noise_at_near_zero_sites():
    # hyperarid: baseline all zero, recent tiny drizzle below min_delta -> not an excursion
    df = make({y: (0.0 if y < 2016 else 0.01) for y in range(2001, 2026)})
    r = analyze_variable(df, min_delta=0.05, **KW)
    assert r.rate_recent == 0


def test_wetter_recent_decade_is_drifting():
    df = make({y: (0.0 if y < 2016 else 1.0) for y in range(2001, 2026)})
    r = analyze_variable(df, min_delta=0.05, **KW)
    assert r.rate_recent == pytest.approx(12.0)
    assert r.drifting


def test_direction_lower_mirrors():
    df = make({y: (5.0 if y < 2016 else 1.0) for y in range(2001, 2026)})
    r = analyze_variable(df, min_delta=0.1, **{**KW, "direction": "lower"})
    assert r.drifting


def test_no_baseline_data_is_reported_not_guessed():
    # like SMAP: starts 2015
    df = make({y: 0.2 for y in range(2015, 2026)})
    r = analyze_variable(df, min_delta=0.01, **KW)
    assert r.change is None and not r.drifting and "baseline" in r.note


def test_single_spike_is_flagged():
    df = make({y: 0 for y in range(2001, 2026)}, month_values=lambda y, m: 2.0 if (y, m) == (2015, 3) else 0.0)
    s = to_series(df)
    thr = monthly_thresholds(s, (2001, 2010), 0.9, 0.05, "higher")
    flags = flag_excursions(s, thr, "higher")
    assert flags[pd.Period("2015-03", "M")]
    assert flags.sum() == 1
