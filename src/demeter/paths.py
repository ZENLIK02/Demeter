"""Every path the pipeline touches, in one place."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = ROOT / "config"
SITES_YAML = CONFIG_DIR / "sites.yaml"
ANALYSIS_YAML = CONFIG_DIR / "analysis.yaml"

CONTRACTS_DIR = ROOT / "contracts"

RAW_DIR = ROOT / "data" / "raw"          # data/raw/<source>/<site_id>.csv (committed)

WEB_DIR = ROOT / "docs"                  # published by GitHub Pages
WEB_DATA_DIR = WEB_DIR / "data"
WEB_SERIES_DIR = WEB_DATA_DIR / "series"


def raw_path(source: str, site_id: str) -> Path:
    return RAW_DIR / source / f"{site_id}.csv"
