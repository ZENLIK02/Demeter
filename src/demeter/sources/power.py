"""NASA POWER (MERRA-2 / GEOS based), monthly point data. No login, global incl. poles.

API: https://power.larc.nasa.gov/docs/services/api/temporal/monthly/
Resolution is coarse (0.5 x 0.625 deg), so it is the fast, always-available baseline;
Earth Engine (gee.py) adds higher-resolution IMERG / MODIS / SMAP.
"""

from __future__ import annotations

import time
from typing import Callable

import pandas as pd
import requests

from demeter.config import Site, Variable
from demeter.sources.base import Source

API = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# our variable id -> (POWER parameter, converter)
PARAMS: dict[str, tuple[str, Callable[[float], float]]] = {
    "precip": ("PRECTOTCORR", lambda x: x),          # mm/day
    "temp": ("T2M", lambda x: x),                    # deg C
    "soil_wetness": ("GWETTOP", lambda x: x),        # 0-1
}

FILL = -999.0


class PowerSource(Source):
    name = "power"
    title = "NASA POWER monthly point data (MERRA-2 based)"
    provider = "NASA Langley Research Center"
    url = "https://power.larc.nasa.gov/"
    notes = "Precipitation (PRECTOTCORR), 2 m air temperature (T2M), surface soil wetness (GWETTOP). ~0.5 deg grid."

    def supports(self, variable: Variable) -> bool:
        return variable.id in PARAMS

    def fetch(self, site: Site, variables: list[Variable], start_year: int, end_year: int) -> pd.DataFrame:
        wanted = [v for v in variables if self.supports(v)]
        if not wanted:
            return pd.DataFrame(columns=["date", "variable", "value", "source"])
        params = {
            "parameters": ",".join(PARAMS[v.id][0] for v in wanted),
            "community": "AG",
            "latitude": site.lat,
            "longitude": site.lon,
            "start": start_year,
            "end": end_year,
            "format": "JSON",
        }
        data = _get_json(params)["properties"]["parameter"]
        rows = []
        for v in wanted:
            param, convert = PARAMS[v.id]
            for key, value in data.get(param, {}).items():
                month = key[4:]
                if month == "13" or value is None or value == FILL:  # "13" = annual mean
                    continue
                rows.append({"date": f"{key[:4]}-{month}", "variable": v.id, "value": convert(float(value)), "source": self.name})
        return pd.DataFrame(rows)


def _get_json(params: dict, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            r = requests.get(API, params=params, timeout=90)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")
