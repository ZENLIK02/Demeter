"""Typed access to config/*.yaml. Code never hard-codes sites, variables or thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from demeter import paths


@dataclass(frozen=True)
class Event:
    id: str
    label: str
    start: str
    end: str
    variable: str
    citation: str = ""
    url: str = ""
    expect_excursion_years: tuple[int, ...] = ()


@dataclass(frozen=True)
class Site:
    id: str
    name: str
    country: str
    lat: float
    lon: float
    polar: bool = False
    analog_for: str = ""
    events: tuple[Event, ...] = ()


@dataclass(frozen=True)
class Variable:
    id: str
    label: str
    unit: str
    direction: str  # "higher" | "lower": which way is NOT Mars-like
    min_delta: float
    source: str
    source_polar: str
    enabled: bool
    why: str = ""

    def source_for(self, site: Site) -> str:
        return self.source_polar if site.polar else self.source


@dataclass(frozen=True)
class StatusRule:
    status: str
    min_share: float


@dataclass(frozen=True)
class Analysis:
    baseline: tuple[int, int]
    recent: tuple[int, int]
    quantile: float
    drift_change: float
    status_rules: tuple[StatusRule, ...]
    variables: tuple[Variable, ...] = field(default_factory=tuple)

    @property
    def enabled_variables(self) -> tuple[Variable, ...]:
        return tuple(v for v in self.variables if v.enabled)

    def variable(self, var_id: str) -> Variable:
        for v in self.variables:
            if v.id == var_id:
                return v
        raise KeyError(f"unknown variable {var_id!r} (see config/analysis.yaml)")


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_sites(path: Path = paths.SITES_YAML) -> tuple[Site, ...]:
    raw = _load_yaml(path)
    sites = []
    for s in raw.get("sites", []):
        events = tuple(
            Event(
                id=e["id"],
                label=e["label"],
                start=str(e["start"]),
                end=str(e["end"]),
                variable=e["variable"],
                citation=e.get("citation", ""),
                url=e.get("url", "") or "",
                expect_excursion_years=tuple(e.get("expect_excursion_years", [])),
            )
            for e in s.get("events", [])
        )
        sites.append(
            Site(
                id=s["id"],
                name=s["name"],
                country=s["country"],
                lat=float(s["lat"]),
                lon=float(s["lon"]),
                polar=bool(s.get("polar", abs(float(s["lat"])) > 60)),
                analog_for=s.get("analog_for", ""),
                events=events,
            )
        )
    ids = [s.id for s in sites]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate site ids in {path.name}: {sorted(dupes)}")
    return tuple(sites)


def load_analysis(path: Path = paths.ANALYSIS_YAML) -> Analysis:
    raw = _load_yaml(path)
    periods = raw["periods"]
    variables = tuple(
        Variable(
            id=vid,
            label=v["label"],
            unit=v["unit"],
            direction=v.get("direction", "higher"),
            min_delta=float(v.get("min_delta", 0.0)),
            source=v["source"],
            source_polar=v.get("source_polar", v["source"]),
            enabled=bool(v.get("enabled", True)),
            why=v.get("why", ""),
        )
        for vid, v in raw["variables"].items()
    )
    for v in variables:
        if v.direction not in ("higher", "lower"):
            raise ValueError(f"variable {v.id}: direction must be 'higher' or 'lower'")
    rules = tuple(
        StatusRule(r["status"], float(r["min_share"]))
        for r in sorted(raw["status_rules"], key=lambda r: -float(r["min_share"]))
    )
    return Analysis(
        baseline=(int(periods["baseline"]["start"]), int(periods["baseline"]["end"])),
        recent=(int(periods["recent"]["start"]), int(periods["recent"]["end"])),
        quantile=float(raw["threshold"]["quantile"]),
        drift_change=float(raw["drift_change_months_per_year"]),
        status_rules=rules,
        variables=variables,
    )
