# Challenge #9: does Expiring Mars fit? (checked 2026-11-14)

Official page: https://www.spaceappschallenge.org/2026/challenges/permanent-moon-base-locations-and-mars/

## What the challenge asks (paraphrased)
- **Identify and characterize** places on Earth that are useful analogs for candidate Moon-base or Mars sites, and show them as a map, visualization or tool.
- Explain **what is analogous and where the analogy breaks down**, and how the site helps Moon/Mars exploration.
- It explicitly says the goal is **not to rediscover well-known analog sites**. It names Antarctica, the Atacama, Iceland and Hawaii as already widely studied, and encourages finding less-studied places with NASA's global Earth data.
- It encourages **processes as well as places**, similarity metrics or rankings, multiple datasets, and using **Moon and Mars data** too.

Resources tab lists: Earthdata Search, Worldview, NASA PDS, LRO (LROC, LOLA, Diviner, Mini-RF), CSA RADARSAT/RCM, ESA Copernicus + Open Science Catalog, JAXA G-Portal.

## Fit of the current plan
| Challenge asks | Expiring Mars today | Gap |
|---|---|---|
| Identify new analog locations | Monitors 13 known sites | **Big gap**: 8 of our 13 sites are the famous ones it says to look beyond |
| Characterize; say where analogy breaks | Per-variable excursions show when a site stops being Mars-like | Good fit |
| Processes, not just places | Climate drift is a process | Good fit |
| Use Moon/Mars data | Mars data used only as a direction (dry, barren, cold) | Weak: no PDS / Mars data in the pipeline |
| Map, visualization or tool | Web map + charts | Good fit |

## Options to close the gap (team decides)
1. **"Expiring Mars → where are the next ones?"** Use the same metrics to scan a global grid for places that are dry, barren and cold today *and* stable over 25 years. Present them as candidate replacement analogs, with the famous sites as the benchmark. This answers "identify" directly and keeps the existing work.
2. **Add a Mars reference.** Compare each site's ranges with Mars surface values (Curiosity REMS or a Mars climate dataset from PDS) for an explicit "similar here / different here" table.
3. **Say plainly that this is a characterization project** and that it covers Mars, not the Moon. This is lowest effort, but leaves Relevance points on the table.

Option 1 reuses the pipeline: a grid of points is just more "sites" in `config/`. It is the strongest answer to the objectives.
