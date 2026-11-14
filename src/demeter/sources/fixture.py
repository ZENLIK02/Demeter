"""Synthetic, deterministic data with the real shape. For tests and offline frontend work.

Never shipped: `export` refuses fixture data unless --allow-fixture is passed.
"""

from __future__ import annotations

import zlib

import numpy as np
import pandas as pd

from demeter.config import Site, Variable
from demeter.sources.base import Source

BASE = {"precip": (1.0, 0.8), "temp": (10.0, 8.0), "soil_wetness": (0.3, 0.1), "ndvi": (0.15, 0.05), "lst": (20.0, 10.0), "soil_moisture": (0.15, 0.05)}


class FixtureSource(Source):
    name = "fixture"
    title = "Synthetic fixture data (development only)"
    provider = "Demeter team"
    url = ""
    notes = "Deterministic random series with a gentle trend. Not real data."

    def supports(self, variable: Variable) -> bool:
        return True

    def fetch(self, site: Site, variables: list[Variable], start_year: int, end_year: int) -> pd.DataFrame:
        dates = pd.period_range(f"{start_year}-01", f"{end_year}-12", freq="M")
        rows = []
        for v in variables:
            rng = np.random.default_rng(zlib.crc32(f"{site.id}:{v.id}".encode()))
            mean, amp = BASE.get(v.id, (1.0, 0.5))
            t = np.arange(len(dates))
            seasonal = amp * np.sin(2 * np.pi * (dates.month.to_numpy() - 1) / 12 + (np.pi if site.lat < 0 else 0))
            trend = (rng.uniform(-0.2, 0.6) * amp) * t / len(t)
            noise = rng.normal(0, amp * 0.25, len(t))
            values = mean + seasonal + trend + noise
            if v.id in ("precip", "soil_wetness", "ndvi", "soil_moisture"):
                values = np.clip(values, 0, None)
            rows += [{"date": str(d), "variable": v.id, "value": float(x), "source": self.name} for d, x in zip(dates, values)]
        return pd.DataFrame(rows)
