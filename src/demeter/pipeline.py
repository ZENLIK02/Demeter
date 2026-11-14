"""Glue: config + raw CSVs -> per-site results. fetch() talks to the network; compute() never does."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from demeter.config import Analysis, Site, Variable
from demeter.excursions import VariableResult, analyze_variable
from demeter.sources import get_source
from demeter.sources.base import read_raw, write_raw

DATA_START_YEAR = 2001


@dataclass
class SiteResult:
    site: Site
    variables: dict[str, VariableResult] = field(default_factory=dict)
    status: str = "no_data"
    drift_share: float = 0.0


def default_end_year() -> int:
    return date.today().year - 1  # last complete year


def fetch(
    sites: tuple[Site, ...],
    analysis: Analysis,
    *,
    source: str,
    variables: list[str] | None = None,
    start_year: int = DATA_START_YEAR,
    end_year: int | None = None,
    log=print,
) -> None:
    """Download raw data for every site whose configured source for a variable is `source`.

    `variables` restricts to ids; disabled variables are fetched too when named explicitly,
    so the Data role can pull new variables before switching them on.
    """
    end_year = end_year or default_end_year()
    src = get_source(source)
    pool = [analysis.variable(v) for v in variables] if variables else list(analysis.enabled_variables)
    for site in sites:
        wanted = [v for v in pool if (v.source_for(site) == source or source == "fixture") and src.supports(v)]
        if not wanted:
            continue
        log(f"[{source}] {site.id}: {', '.join(v.id for v in wanted)} {start_year}-{end_year}")
        df = src.fetch(site, wanted, start_year, end_year)
        if df.empty:
            log(f"  ! no rows returned for {site.id}")
            continue
        path = write_raw(df, source, site.id)
        log(f"  -> {path.relative_to(path.parents[3])} ({len(df)} rows)")


def compute(sites: tuple[Site, ...], analysis: Analysis, *, source_override: str | None = None) -> list[SiteResult]:
    results = []
    for site in sites:
        res = SiteResult(site)
        for var in analysis.enabled_variables:
            source = source_override or var.source_for(site)
            raw = read_raw(source, site.id)
            rows = raw[raw["variable"] == var.id]
            if rows.empty:
                continue
            res.variables[var.id] = _analyze(rows, var, source, analysis)
        _assign_status(res, analysis)
        results.append(res)
    return results


def _analyze(rows, var: Variable, source: str, analysis: Analysis) -> VariableResult:
    return analyze_variable(
        rows,
        variable=var.id,
        source=source,
        baseline=analysis.baseline,
        recent=analysis.recent,
        quantile=analysis.quantile,
        min_delta=var.min_delta,
        direction=var.direction,
        drift_change=analysis.drift_change,
    )


def _assign_status(res: SiteResult, analysis: Analysis) -> None:
    scored = [v for v in res.variables.values() if v.change is not None]
    if not scored:
        res.status, res.drift_share = "no_data", 0.0
        return
    share = sum(v.drifting for v in scored) / len(scored)
    res.drift_share = round(share, 3)
    for rule in analysis.status_rules:  # sorted high -> low min_share
        if share >= rule.min_share:
            res.status = rule.status
            return
