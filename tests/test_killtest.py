"""The method must catch the documented Atacama 2015-2017 rains in the committed real data."""

import pytest

from demeter import killtest, paths
from demeter.config import load_analysis, load_sites
from demeter.pipeline import compute


@pytest.mark.killtest
def test_atacama_rains_are_caught():
    if not (paths.RAW_DIR / "power" / "atacama_yungay.csv").exists():
        pytest.skip("no data/raw/power yet: run `python -m demeter fetch --source power`")
    results = compute(load_sites(), load_analysis())
    checks = killtest.run(results)
    assert checks, "no events with expect_excursion_years configured"
    failed = [c for c in checks if not c.passed]
    assert not failed, f"kill test failed: {failed}"
