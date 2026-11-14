// Entry point: load data, mount components, restore selection from the URL hash (#site=<id>).

import { loadSummary } from "./data.js";
import { getState, setState, subscribe } from "./store.js";
import { escapeHtml } from "./util.js";
import * as headline from "./components/headline.js";
import * as map from "./components/map.js";
import * as panel from "./components/panel.js";
import * as ranking from "./components/ranking.js";
import * as toggle from "./components/variable-toggle.js";

const components = [
  [headline, "headline"],
  [toggle, "variable-toggle"],
  [map, "map"],
  [panel, "panel"],
  [ranking, "ranking"],
];

async function boot() {
  let summary;
  try {
    summary = await loadSummary();
  } catch (err) {
    document.getElementById("headline").innerHTML =
      `<div class="stat"><div class="label">Could not load data/sites.json. Run <code>python -m demeter run</code>. (${escapeHtml(err.message)})</div></div>`;
    return;
  }
  for (const [mod, id] of components) mod.mount(document.getElementById(id), { getState, setState, subscribe });

  const fromHash = new URLSearchParams(location.hash.slice(1)).get("site");
  setState({ summary, selectedSiteId: summary.sites.some((s) => s.id === fromHash) ? fromHash : null });

  subscribe((s, patch) => {
    if ("selectedSiteId" in patch && s.selectedSiteId) history.replaceState(null, "", `#site=${s.selectedSiteId}`);
  });
  document.getElementById("generated").textContent = `Data generated ${summary.generated_at.slice(0, 10)}`;
}

boot();
