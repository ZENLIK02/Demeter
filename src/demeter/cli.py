"""Command line: python -m demeter <command>   (or `demeter <command>` after pip install -e .)

  fetch     download raw data          --source power|gee|fixture  [--site ID] [--var ID]
  analyze   print per-site results     [--site ID]
  killtest  check the method against documented events (Atacama 2015-2017)
  export    write docs/data/*.json     [--allow-fixture]
  run       fetch(power) + killtest + export, the one-shot refresh
  serve     preview the web app at http://localhost:8000
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys

from demeter import export as export_mod
from demeter import killtest, paths, pipeline
from demeter.config import load_analysis, load_sites


def _sites(ids: list[str] | None):
    sites = load_sites()
    if not ids:
        return sites
    unknown = set(ids) - {s.id for s in sites}
    if unknown:
        sys.exit(f"unknown site id(s): {sorted(unknown)}")
    return tuple(s for s in sites if s.id in ids)


def cmd_fetch(a) -> int:
    pipeline.fetch(_sites(a.site), load_analysis(), source=a.source, variables=a.var, start_year=a.start, end_year=a.end)
    return 0


def cmd_analyze(a) -> int:
    analysis = load_analysis()
    results = pipeline.compute(_sites(a.site), analysis, source_override=a.source)
    for r in results:
        print(f"{r.site.id:22s} {r.status:9s} drift_share={r.drift_share:.2f}")
        for vid, v in r.variables.items():
            chg = "n/a" if v.change is None else f"{v.change:+.2f}"
            print(f"    {vid:14s} {v.source:7s} base={v.rate_baseline} recent={v.rate_recent} change={chg} {'DRIFT' if v.drifting else ''} {v.note}")
    return 0


def cmd_killtest(a) -> int:
    results = pipeline.compute(load_sites(), load_analysis(), source_override=a.source)
    return 0 if killtest.report(killtest.run(results)) else 1


def cmd_export(a) -> int:
    analysis = load_analysis()
    results = pipeline.compute(load_sites(), analysis, source_override=a.source)
    written = export_mod.export(results, analysis, allow_fixture=a.allow_fixture)
    print(f"wrote {len(written)} files to {paths.WEB_DATA_DIR.relative_to(paths.ROOT)}/")
    return 0


def cmd_run(a) -> int:
    sites, analysis = load_sites(), load_analysis()
    if not a.no_fetch:
        pipeline.fetch(sites, analysis, source="power")
    results = pipeline.compute(sites, analysis)
    killtest.report(killtest.run(results))
    written = export_mod.export(results, analysis)
    print(f"wrote {len(written)} files to {paths.WEB_DATA_DIR.relative_to(paths.ROOT)}/")
    return 0


def cmd_serve(a) -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(paths.WEB_DIR))
    with socketserver.TCPServer(("", a.port), handler) as httpd:
        print(f"serving {paths.WEB_DIR} at http://localhost:{a.port}  (Ctrl+C to stop)")
        httpd.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="demeter", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="download raw data")
    f.add_argument("--source", required=True, help="power | gee | fixture")
    f.add_argument("--site", action="append", help="site id (repeatable); default all")
    f.add_argument("--var", action="append", help="variable id (repeatable); default enabled ones")
    f.add_argument("--start", type=int, default=pipeline.DATA_START_YEAR)
    f.add_argument("--end", type=int, default=None)
    f.set_defaults(fn=cmd_fetch)

    for name, fn, helptext in (("analyze", cmd_analyze, "print results"), ("killtest", cmd_killtest, "validate against events"), ("export", cmd_export, "write docs/data")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("--source", default=None, help="read every variable from this source (e.g. fixture)")
        if name == "analyze":
            s.add_argument("--site", action="append")
        if name == "export":
            s.add_argument("--allow-fixture", action="store_true", help="allow fake data (local UI work only)")
        s.set_defaults(fn=fn)

    r = sub.add_parser("run", help="fetch(power) + killtest + export")
    r.add_argument("--no-fetch", action="store_true", help="reuse data/raw, skip downloads")
    r.set_defaults(fn=cmd_run)

    sv = sub.add_parser("serve", help="preview docs/ locally")
    sv.add_argument("--port", type=int, default=8000)
    sv.set_defaults(fn=cmd_serve)

    a = p.parse_args(argv)
    return a.fn(a)
