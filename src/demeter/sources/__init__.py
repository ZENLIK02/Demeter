"""Source registry. Add a dataset: write sources/<name>.py with a Source subclass, register it here."""

from __future__ import annotations

from demeter.sources.base import Source
from demeter.sources.fixture import FixtureSource
from demeter.sources.gee import GeeSource
from demeter.sources.power import PowerSource

REGISTRY: dict[str, type[Source]] = {
    PowerSource.name: PowerSource,
    GeeSource.name: GeeSource,
    FixtureSource.name: FixtureSource,
}


def get_source(name: str) -> Source:
    try:
        return REGISTRY[name]()
    except KeyError:
        raise KeyError(f"unknown source {name!r}; known: {sorted(REGISTRY)}") from None
