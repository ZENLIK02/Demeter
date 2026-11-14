// Tiny shared state. Components never call each other: they read state and subscribe.
// Adding a feature = a new component that subscribes; nothing else changes.

const state = {
  summary: null,        // docs/data/sites.json
  selectedSiteId: null, // site the panel shows
  variable: "all",      // "all" = colour by site status, else a variable id
  year: null,           // null = decade comparison; a number = colour the map by that year
  yearCounts: null,     // { siteId: { variableId: { year: excursion months } } }, set by year-slider
};

const listeners = new Set();

export function getState() {
  return state;
}

export function setState(patch) {
  Object.assign(state, patch);
  for (const fn of listeners) fn(state, patch);
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
