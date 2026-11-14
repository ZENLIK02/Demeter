"""The source plug-in interface and the raw-CSV contract (contracts/raw_series.md).

A source turns (site, variables, years) into a long DataFrame:
    date (YYYY-MM) | variable | value | source
Adding a new dataset = one new module in this package + a name in config/analysis.yaml.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from demeter import paths
from demeter.config import Site, Variable

RAW_COLUMNS = ["date", "variable", "value", "source"]


class Source(ABC):
    #: short id used in config/analysis.yaml and data/raw/<name>/
    name: str = ""
    #: shown on the web app's Data page
    title: str = ""
    provider: str = ""
    url: str = ""
    notes: str = ""

    @abstractmethod
    def supports(self, variable: Variable) -> bool:
        """True when this source knows how to produce `variable`."""

    @abstractmethod
    def fetch(self, site: Site, variables: list[Variable], start_year: int, end_year: int) -> pd.DataFrame:
        """Return monthly values in long format (RAW_COLUMNS), units already converted."""


def validate_raw(df: pd.DataFrame, where: str = "") -> pd.DataFrame:
    missing = [c for c in RAW_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{where}: raw series missing columns {missing}")
    df = df[RAW_COLUMNS].copy()
    bad_dates = ~df["date"].astype(str).str.fullmatch(r"\d{4}-\d{2}")
    if bad_dates.any():
        raise ValueError(f"{where}: dates must be YYYY-MM, got e.g. {df.loc[bad_dates, 'date'].iloc[0]!r}")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    if df.duplicated(["date", "variable"]).any():
        raise ValueError(f"{where}: duplicate (date, variable) rows")
    return df.sort_values(["variable", "date"]).reset_index(drop=True)


def write_raw(df: pd.DataFrame, source: str, site_id: str) -> Path:
    """Merge into data/raw/<source>/<site_id>.csv (new rows win), so variables can be fetched separately."""
    path = paths.raw_path(source, site_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = validate_raw(df, str(path))
    if path.exists():
        old = validate_raw(pd.read_csv(path, dtype={"date": str}), str(path))
        old = old[~old["variable"].isin(df["variable"].unique())]
        df = pd.concat([old, df], ignore_index=True)
    df = validate_raw(df, str(path))
    df.to_csv(path, index=False, float_format="%.6g")
    return path


def read_raw(source: str, site_id: str) -> pd.DataFrame:
    path = paths.raw_path(source, site_id)
    if not path.exists():
        return pd.DataFrame(columns=RAW_COLUMNS)
    return validate_raw(pd.read_csv(path, dtype={"date": str}), str(path))
