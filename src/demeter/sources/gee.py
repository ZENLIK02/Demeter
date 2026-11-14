"""Google Earth Engine: IMERG rainfall, MODIS NDVI / LST, SMAP soil moisture.

Status: written against the GEE Python API but NOT yet run (needs a signed-in account).
Before trusting it, the Data role should:
  1. pip install -e ".[gee]"  then  earthengine authenticate
  2. set EE_PROJECT=<your Cloud project id>
  3. collection ids + bands below were checked in the GEE Data Catalog on 2026-11-14
     (IMERG monthly V07: mm/hr, ends 2025-09; SMAP L4 v008 starts 2015-03-31)
  4. python -m demeter fetch --source gee --site atacama_yungay   (one site first)

Each variable is reduced to a monthly mean over a buffer around the site.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from demeter.config import Site, Variable
from demeter.sources.base import Source


@dataclass(frozen=True)
class Collection:
    id: str
    band: str
    scale_m: int
    convert: Callable[[float], float]
    monthly: bool = False  # collection already holds one image per month
    buffer_m: int = 5000


# our variable id -> collection. VERIFY ids/bands in the GEE Data Catalog.
COLLECTIONS: dict[str, Collection] = {
    # IMERG monthly precipitation, mm/hr -> mm/day. Unreliable poleward of ~60 deg.
    "precip": Collection("NASA/GPM_L3/IMERG_MONTHLY_V07", "precipitation", 11132, lambda x: x * 24, monthly=True, buffer_m=15000),
    # MODIS 16-day NDVI (250 m), scale factor 0.0001
    "ndvi": Collection("MODIS/061/MOD13Q1", "NDVI", 250, lambda x: x * 0.0001),
    # MODIS 8-day daytime LST (1 km), Kelvin * 0.02 -> deg C
    "lst": Collection("MODIS/061/MOD11A2", "LST_Day_1km", 1000, lambda x: x * 0.02 - 273.15),
    # SMAP L4 3-hourly surface soil moisture (9 km), m3/m3. Starts 2015.
    "soil_moisture": Collection("NASA/SMAP/SPL4SMGP/008", "sm_surface", 11000, lambda x: x, buffer_m=15000),
}


class GeeSource(Source):
    name = "gee"
    title = "Google Earth Engine: GPM IMERG, MODIS MOD13Q1 / MOD11A2, SMAP L4"
    provider = "NASA (via Google Earth Engine)"
    url = "https://developers.google.com/earth-engine/datasets"
    notes = "Monthly means over a 5-15 km buffer around each site."

    def supports(self, variable: Variable) -> bool:
        return variable.id in COLLECTIONS

    def fetch(self, site: Site, variables: list[Variable], start_year: int, end_year: int) -> pd.DataFrame:
        ee = _init_ee()
        rows = []
        for v in variables:
            if not self.supports(v):
                continue
            col = COLLECTIONS[v.id]
            region = ee.Geometry.Point([site.lon, site.lat]).buffer(col.buffer_m)
            for date, value in _monthly_means(ee, col, region, start_year, end_year):
                rows.append({"date": date, "variable": v.id, "value": col.convert(value), "source": self.name})
        return pd.DataFrame(rows)


def _init_ee():
    try:
        import ee  # type: ignore
    except ImportError as exc:
        raise RuntimeError('Earth Engine not installed: pip install -e ".[gee]"') from exc
    project = os.environ.get("EE_PROJECT")
    ee.Initialize(project=project) if project else ee.Initialize()
    return ee


def _monthly_means(ee, col: Collection, region, start_year: int, end_year: int):
    """Yield (YYYY-MM, value) with one server round-trip per variable."""
    ic = ee.ImageCollection(col.id).select(col.band)
    months = ee.List.sequence(0, (end_year - start_year + 1) * 12 - 1)
    origin = ee.Date.fromYMD(start_year, 1, 1)

    def per_month(n):
        start = origin.advance(n, "month")
        img = ic.filterDate(start, start.advance(1, "month")).mean()
        stat = img.reduceRegion(ee.Reducer.mean(), region, col.scale_m, maxPixels=1e9, bestEffort=True)
        return ee.Feature(None, {"date": start.format("YYYY-MM"), "value": stat.get(col.band)})

    feats = ee.FeatureCollection(months.map(per_month)).getInfo()["features"]
    for f in feats:
        p = f["properties"]
        if p.get("value") is not None:
            yield p["date"], float(p["value"])
