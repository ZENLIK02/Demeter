# App plan: Expiring Mars

What the web app looks like, what it does, and the order we build it.
Schedule times come from the team hand-off (Thailand time, 14–15 Nov 2026). Feature freeze **Sun 12:00**. Submit **Sun 20:00**.

> **Open decision (blocks step 6):** the official challenge asks for *new* analog sites, not just famous ones
> (see [challenge-09-fit.md](challenge-09-fit.md)). If the team picks **Option 1 "where are the next ones?"**, build step 6.
> If not, skip step 6 and say clearly on the Method page that this is a characterization project.

## 1. What it looks like

One page plus a Method page. Desktop layout (phones stack everything in one column):

```
+--------------------------------------------------------------------------------+
| (o) Expiring Mars          "Are our Mars training grounds expiring?"   Map | Method |
+--------------------------------------------------------------------------------+
| [ X of 13 sites ]  [ N leaving on half+ ]  [ 3 NASA variables ]  [ 2001–2025 ] |  <- headline
+-----------------------------------------------+--------------------------------+
| 13 Mars-analog test sites                     | ATACAMA (YUNGAY)    [Leaving]  |
| Colour by: (Overall)(Rainfall)(Temp)(Soil)    | Chile · Mars hyperarid soils   |
|                                               | <one-line verdict from data;  |
|        world map, one dot per site            |  sketch numbers are examples> |
|        green / amber / red / grey             | +----------------------------+ |
|                                               | | Rare rains 2015-2017,      | |
|        [ year slider 2001 ----o---- 2025 ]    | | microbe die-off (2018)     | |
|                                               | +----------------------------+ |
| legend: o stable  o drifting  o leaving       | Variable | 2001-10 | 2016-25 | |
|                                               | Rainfall |   0.5   |   0.9   | |
|                                               | Temp ... |         |         | |
|                                               | [chart: rainfall 2001-2025, | |
|                                               |  normal band, red dots =    | |
|                                               |  excursion months]          | |
+-----------------------------------------------+--------------------------------+
| Which sites are drifting most?  (sortable table, click a row = select site)    |
| Site | Country | Status | Rainfall | Temp | Soil | Avg change                   |
+--------------------------------------------------------------------------------+
| [Option 1 only] Where are the next Mars analogs?  map + top 10 candidates      |
+--------------------------------------------------------------------------------+
| Data generated 2026-11-15 · NASA open data · MIT · not endorsed by NASA         |
+--------------------------------------------------------------------------------+
```

**Method page** (`docs/method.html`): what an excursion is (3 steps in plain English), the datasets with links,
what Earth cannot reproduce (gravity, vacuum, thin atmosphere, radiation), limits of our data, AI declaration.

**30-second demo path** (video and live judging):
1. Map and headline number.
2. Click Atacama. The 2015–2017 spike sits under its evidence label.
3. Drag the year slider; the dots change colour.
4. (Option 1) Show the top candidate new analog.
5. Close on "Are our Mars training grounds expiring?"

## 2. Features

Status: ✅ done · 🟡 started · ⬜ not started

### Must-have (the demo fails without these)
| # | Feature | Owner | Status | Done when |
|---|---|---|---|---|
| M1 | Real data for 13 sites + kill test | Data, Science | ✅ | `python -m demeter killtest` passes (it does: Atacama 2015-03, 2017-06) |
| M2 | Tuned index + headline number | Science | 🟡 | Thresholds in `config/analysis.yaml` give a result the team can defend (today 11/13 "leaving", mostly from temperature) |
| M3 | World map, dots coloured by status | Frontend | ✅ | `components/map.js`; clicking a dot selects the site |
| M4 | Site panel: name, verdict, metrics table | Frontend | ✅ | `components/panel.js` reads `sites.json` |
| M5 | Time-series chart per variable | Frontend | ✅ | `components/chart.js`: value line, threshold line, red excursion dots, baseline/recent shading |
| M6 | Atacama evidence label on the chart | Frontend, Story | 🟡 (label shown; citation link still TODO in `config/sites.yaml`) | Event band from `config/sites.yaml` with citation and link |
| M7 | Headline strip | Frontend | ✅ | `components/headline.js` (written; needs real numbers from M2) |
| M8 | Method & limits page | Story | ✅ (team to review wording) | `docs/method.html`, written from config and `sites.json` |
| M9 | NASA data list + AI declaration | Story | 🟡 (on Method page; project page still to write) | On the Method page and the project page |
| M10 | Live on GitHub Pages | ZENLIK02 | ⬜ | Link opens in an incognito window with no login |

### Should-have (add only if must-haves are done)
| # | Feature | Owner | Status | Notes |
|---|---|---|---|---|
| S1 | Ranking table, click row to select | Frontend | ✅ | `components/ranking.js`; covers the "identify" angle a little |
| S2 | "Colour by" variable toggle | Frontend | ✅ | `components/variable-toggle.js` (written) |
| S3 | Year slider recolours the map | Frontend | ⬜ | Needs per-year excursion counts (already in the series JSON) |
| S4 | Polar-site badge ("IMERG unreliable >60°") | Frontend | ⬜ | Shows the team knows the data's limits |
| S5 | Download CSV/JSON buttons | Frontend | ⬜ | Links to `data/raw` and `docs/data` on GitHub |
| S6 | Higher-resolution data via Earth Engine (NDVI, LST, IMERG) | Data | ⬜ | Needs an Earth Engine account; turn on in `config/analysis.yaml` |

### Option 1 only: "Where are the next ones?"
| # | Feature | Owner | Notes |
|---|---|---|---|
| N1 | Candidate grid in config | Science | A grid of points over drylands and polar areas becomes extra "sites" (same pipeline) |
| N2 | Mars-likeness + stability ranking | Science | Dry, barren, cold today **and** few excursions over 25 years |
| N3 | Candidates section on the page | Frontend | Map layer + top 10 list, famous sites shown as the benchmark |

### Stretch (only if everything above is stable)
"Add your own site" (needs live Earth Engine, so it's a roadmap item), Moon analogs, a Mars reference table from PDS / Curiosity REMS data, mobile polish beyond "doesn't break".

### Leave out
Live Earth Engine queries, user accounts or a backend, ML predictions.

## 3. Build order

Each step lists what must be finished before it can start. Steps on the same line run in parallel.

| Step | When | Data | Science | Frontend | Story |
|---|---|---|---|---|---|
| 0 | **Now** | | **Decide Option 1 or not** (whole team, 15 min) | | |
| 1 | Sat → 20:00 | Earth Engine sign-up; test one site with `fetch --source gee` | M2: tune thresholds; kill test still passes | Build M3, M4 on fixture data (`export --source fixture --allow-fixture`) | Ask LINE @droneth about team size and Global slots; fix the TODO phys.org link |
| 2 | Sat 20:00 | | **Checkpoint:** kill test + defensible headline, or switch to the backup plan (#8) | | |
| 3 | Sat 20:00 → Sun 02:00 | S6: Earth Engine data for all sites (if access works) | N1, N2 (Option 1) | M5, M6, M7 | M8 draft, project page draft |
| 4 | Sun 02:00 → 08:00 | Rest in shifts | | | |
| 5 | Sun 08:00 → 12:00 | Final `python -m demeter run`; commit `docs/data` | Check every number on the page against `sites.json` | S1 → S2 → S3 → S4 (in that order, stop at 12:00); N3 if Option 1 | M9; slides outline |
| 6 | **Sun 12:00** | | | **Feature freeze.** Fixes only from here. | |
| 7 | Sun 12:00 → 14:00 | M10: confirm Pages is live | Final numbers to Story | Fix bugs; phone check | Record the demo path |
| 8 | Sun 14:00 → 19:00 | | | | Video (30 s, English subtitles, TTS voice), 7 slides, project page |
| 9 | Sun 19:00 → 20:00 | Whole team: rules checklist in [CONTRIBUTING.md](../CONTRIBUTING.md), incognito link test | | | |
| 10 | **Sun 20:00** | **Submit** (the real deadline is 23:59, but submit at 20:00 as planned) | | | |

If the team has 3 people, the Frontend person also takes Story from Sun 14:00 (as in the hand-off).

## 4. Definition of done for any feature
- Works on the live link, not just on a laptop.
- Uses only numbers from `docs/data/` (no hard-coded results).
- `pytest -q` passes, and CI is green.
- Merged into `main` in a small PR.
