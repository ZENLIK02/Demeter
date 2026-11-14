"""Results -> docs/data/*.json, validated against contracts/*.schema.json before writing.

The web app only ever reads these files, so frontend and pipeline can change independently
as long as the contract holds.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from demeter import paths
from demeter.config import Analysis
from demeter.pipeline import SiteResult
from demeter.sources import REGISTRY


def _schema(name: str) -> dict:
    return json.loads((paths.CONTRACTS_DIR / name).read_text(encoding="utf-8"))


def build_summary(results: list[SiteResult], analysis: Analysis) -> dict:
    used_sources = sorted({v.source for r in results for v in r.variables.values()})
    used_vars = [v for v in analysis.enabled_variables if any(v.id in r.variables for r in results)]
    sites = []
    for r in results:
        s = r.site
        sites.append(
            {
                "id": s.id,
                "name": s.name,
                "country": s.country,
                "lat": s.lat,
                "lon": s.lon,
                "polar": s.polar,
                "analog_for": s.analog_for,
                "status": r.status,
                "drift_share": r.drift_share,
                "events": [
                    {"id": e.id, "label": e.label, "start": e.start, "end": e.end, "variable": e.variable, "citation": e.citation, "url": e.url}
                    for e in s.events
                ],
                "metrics": {
                    vid: {
                        "rate_baseline": v.rate_baseline,
                        "rate_recent": v.rate_recent,
                        "change": v.change,
                        "drifting": v.drifting,
                        "source": v.source,
                        **({"note": v.note} if v.note else {}),
                    }
                    for vid, v in r.variables.items()
                },
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": {
            "baseline": list(analysis.baseline),
            "recent": list(analysis.recent),
            "quantile": analysis.quantile,
            "drift_change_months_per_year": analysis.drift_change,
        },
        "headline": {
            "sites_total": len(results),
            "sites_drifting": sum(r.status in ("drifting", "leaving") for r in results),
            "sites_leaving": sum(r.status == "leaving" for r in results),
        },
        "variables": [
            {
                "id": v.id,
                "label": v.label,
                "unit": v.unit,
                "direction": v.direction,
                "why": v.why,
                "sources": sorted({r.variables[v.id].source for r in results if v.id in r.variables}),
            }
            for v in used_vars
        ],
        "data_sources": [
            {"id": n, "name": REGISTRY[n].title, "provider": REGISTRY[n].provider, "url": REGISTRY[n].url, "notes": REGISTRY[n].notes}
            for n in used_sources
        ],
        "sites": sites,
    }


def build_series(r: SiteResult) -> dict:
    return {
        "site_id": r.site.id,
        "variables": {
            vid: {
                "source": v.source,
                "unit": "",
                "dates": v.dates,
                "values": v.values,
                "threshold": v.threshold,
                "excursion": v.excursion,
                "excursions_per_year": v.excursions_per_year,
            }
            for vid, v in r.variables.items()
        },
    }


def export(results: list[SiteResult], analysis: Analysis, *, allow_fixture: bool = False, out_dir: Path = paths.WEB_DATA_DIR) -> list[Path]:
    if not allow_fixture and any(v.source == "fixture" for r in results for v in r.variables.values()):
        raise RuntimeError("refusing to publish fixture (fake) data; pass --allow-fixture for local UI work")
    units = {v.id: v.unit for v in analysis.variables}
    summary = build_summary(results, analysis)
    jsonschema.validate(summary, _schema("sites.schema.json"))

    series_schema = _schema("series.schema.json")
    written = []
    series_dir = out_dir / "series"
    series_dir.mkdir(parents=True, exist_ok=True)
    for old in series_dir.glob("*.json"):
        old.unlink()
    for r in results:
        doc = build_series(r)
        for vid, v in doc["variables"].items():
            v["unit"] = units.get(vid, "")
        jsonschema.validate(doc, series_schema)
        path = series_dir / f"{r.site.id}.json"
        path.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")
        written.append(path)

    path = out_dir / "sites.json"
    path.write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    written.append(path)
    return written
