# Contract: raw series CSV

Every data source writes one CSV per site:

    data/raw/<source>/<site_id>.csv

| column     | type            | example        | notes                                   |
|------------|-----------------|----------------|-----------------------------------------|
| `date`     | `YYYY-MM`       | `2015-03`      | one row per month per variable          |
| `variable` | string          | `precip`       | an id from `config/analysis.yaml`       |
| `value`    | float           | `0.42`         | already in the unit the config declares |
| `source`   | string          | `power`        | the source module name                  |

Rules
- Long format (one row per month x variable), so a source can add variables without touching others.
- Values are monthly means in the config's unit. Convert units inside the source module.
- Missing months are simply absent. Never write a fill value like -999.
- Files are committed to git, so teammates without Earth Engine access can still run the analysis.

`src/demeter/sources/base.py` enforces this (`validate_raw`).
