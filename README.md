# Expiring Mars

**We test Mars rovers in places that look like Mars. Earth is warming. Are our Mars training grounds expiring?**

NASA Space Apps Challenge 2026, challenge #9 (Earth analogs for Moon bases and Mars).
Live site: https://zenlik02.github.io/Demeter/ (once GitHub Pages is on)

## Quick start (Windows, Git Bash or PowerShell)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m demeter run        # download NASA POWER data, kill test, write docs/data
.venv/Scripts/python -m demeter serve      # open http://localhost:8000
.venv/Scripts/python -m pytest -q          # tests
```

On macOS/Linux use `.venv/bin/python`.

## How it works

1. `config/` holds the sites, variables and thresholds.
2. `src/demeter/sources/` downloads monthly NASA data into `data/raw/` (committed).
3. `src/demeter/excursions.py` compares each site with its own 2001–2010 normal and counts "excursion months" (wetter, greener or warmer than normal).
4. `src/demeter/export.py` writes `docs/data/*.json`, checked against `contracts/`.
5. `docs/` is a static website served by GitHub Pages. It never contacts NASA or Earth Engine.

See [CONTRIBUTING.md](CONTRIBUTING.md) for roles and the dev loop.

## NASA data used
- NASA POWER (MERRA-2 based): precipitation, air temperature, surface soil wetness
- Planned via Google Earth Engine: GPM IMERG, MODIS MOD13Q1 NDVI, MODIS MOD11A2 LST, SMAP L4

## License
MIT. Not affiliated with or endorsed by NASA.
