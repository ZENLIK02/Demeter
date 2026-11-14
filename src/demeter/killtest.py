"""Kill test: does the method catch real, documented events (config/sites.yaml `events`)?

Pass = every year listed in an event's expect_excursion_years has >= 1 excursion month
for that event's variable. If Atacama 2015-2017 is not caught, fix the index before
building anything else (team plan: deadline Saturday 20:00).
"""

from __future__ import annotations

from dataclasses import dataclass

from demeter.pipeline import SiteResult


@dataclass
class Check:
    site: str
    event: str
    variable: str
    year: int
    excursions: int | None

    @property
    def passed(self) -> bool:
        return bool(self.excursions)


def run(results: list[SiteResult]) -> list[Check]:
    checks = []
    for r in results:
        for e in r.site.events:
            v = r.variables.get(e.variable)
            for year in e.expect_excursion_years:
                n = None if v is None else v.excursions_per_year.get(str(year), 0)
                checks.append(Check(r.site.id, e.id, e.variable, year, n))
    return checks


def report(checks: list[Check], log=print) -> bool:
    if not checks:
        log("kill test: no events with expect_excursion_years in config/sites.yaml")
        return False
    for c in checks:
        mark = "PASS" if c.passed else "FAIL"
        got = "no data" if c.excursions is None else f"{c.excursions} excursion month(s)"
        log(f"  {mark}  {c.site} / {c.variable} / {c.year}: {got}")
    ok = all(c.passed for c in checks)
    log("kill test: PASSED" if ok else "kill test: FAILED - fix the index before building more")
    return ok
