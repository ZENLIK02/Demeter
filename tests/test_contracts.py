"""Config + export must always satisfy contracts/*.schema.json (uses fixture data, no network)."""

import json

import pytest

from demeter import paths
from demeter.config import load_analysis, load_sites
from demeter.export import export
from demeter.pipeline import fetch, compute


def test_config_loads():
    sites, analysis = load_sites(), load_analysis()
    assert len(sites) >= 1
    assert analysis.enabled_variables


def test_fixture_export_matches_contracts(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "RAW_DIR", tmp_path / "raw")
    sites, analysis = load_sites()[:3], load_analysis()
    fetch(sites, analysis, source="fixture", log=lambda *_: None)
    results = compute(sites, analysis, source_override="fixture")
    out = tmp_path / "web"
    written = export(results, analysis, allow_fixture=True, out_dir=out)  # validates against schemas
    summary = json.loads((out / "sites.json").read_text(encoding="utf-8"))
    assert summary["headline"]["sites_total"] == 3
    assert len(written) == 4


def test_export_refuses_fixture_data(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "RAW_DIR", tmp_path / "raw")
    sites, analysis = load_sites()[:1], load_analysis()
    fetch(sites, analysis, source="fixture", log=lambda *_: None)
    results = compute(sites, analysis, source_override="fixture")
    with pytest.raises(RuntimeError, match="fixture"):
        export(results, analysis, out_dir=tmp_path / "web")
