# Working on Expiring Mars

## Roles own folders
Lanes only meet through `contracts/`. If you need to change a contract, tell the team first.

| Role | Owns | Starts from |
|---|---|---|
| Data | `src/demeter/sources/`, `data/raw/` | `contracts/raw_series.md` |
| Science | `src/demeter/excursions.py`, `config/analysis.yaml`, `tests/` | committed `data/raw/` |
| Frontend | `docs/` (except `docs/data/`) | `contracts/*.schema.json`; fake data via `export --allow-fixture` |
| Story | `story/`, `docs/method.html` text | `config/`, `docs/data/sites.json` |

`docs/data/` is generated. Never edit it by hand; run `python -m demeter export`.

## Branches
- One small branch per change: `data/gee-ndvi`, `science/threshold-tuning`, `web/ranking-table`, `story/slides`.
- Open a PR into `main` early. CI runs the tests and the kill test.
- Merge often (every 1–2 hours). Small merges are the fast path; big ones cause conflicts.

## Dev loop
| I changed… | Run | Time |
|---|---|---|
| config or science code | `python -m demeter run --no-fetch` then `pytest -q` | seconds |
| frontend | keep `python -m demeter serve` running, refresh the browser | instant |
| a data source | `python -m demeter fetch --source <name> --site atacama_yungay` first, then all sites | minutes |
| frontend, before real data exists | `python -m demeter fetch --source fixture` then `python -m demeter export --source fixture --allow-fixture` | seconds |

Don't commit fixture JSON into `docs/data/`. `export` refuses fake data unless `--allow-fixture` is passed.

## Scaling
- **New site:** add an entry to `config/sites.yaml`.
- **New variable:** add it to `config/analysis.yaml` and map it in a source module.
- **New dataset:** add `src/demeter/sources/<name>.py` (a `Source` subclass) and register it in `sources/__init__.py`.
- **New UI feature:** add `docs/assets/js/components/<name>.js` exporting `mount(el, store)`, then add it to `main.js`.

## Rules that disqualify (check before submitting)
- English everywhere. Links open without a login.
- No faces or voices of anyone under 18. AI-generated images and video need a watermark.
- No NASA logo. MIT license stays in the repo.
- List every NASA dataset used, and declare all AI use (including TTS and coding help).
