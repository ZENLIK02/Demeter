// Year slider: recolours the map by excursion months in ONE year.
// Far right = "All years" (the decade comparison, the default).

import { loadSeries } from "../data.js";

export function mount(el, { subscribe, setState }) {
  let built = false;
  let counts = null; // { siteId: { variableId: { "2015": n } } }

  async function loadCounts(sites) {
    if (!counts) {
      const all = await Promise.all(sites.map((s) => loadSeries(s.id)));
      counts = {};
      for (const doc of all) {
        counts[doc.site_id] = Object.fromEntries(Object.entries(doc.variables).map(([vid, v]) => [vid, v.excursions_per_year || {}]));
      }
    }
    return counts;
  }

  subscribe((s) => {
    if (!s.summary || built) return;
    built = true;
    const y0 = s.summary.method.baseline[0];
    const y1 = s.summary.method.recent[1];
    el.innerHTML = `<label for="year-range">Year</label>
      <input id="year-range" type="range" min="${y0}" max="${y1 + 1}" value="${y1 + 1}" step="1">
      <output for="year-range">All years</output>`;
    const input = el.querySelector("input");
    const out = el.querySelector("output");
    input.addEventListener("input", async () => {
      const year = Number(input.value);
      if (year > y1) {
        out.textContent = "All years";
        setState({ year: null });
        return;
      }
      out.textContent = String(year);
      setState({ year, yearCounts: await loadCounts(s.summary.sites) });
    });
  });
}

/** Status of a site in one year: most excursion months among the chosen variable(s). */
export function yearStatus(site, s) {
  const per = s.yearCounts?.[site.id];
  if (!per) return "no_data";
  const vals = s.variable === "all" ? Object.values(per).map((v) => v[s.year] ?? 0) : [per[s.variable]?.[s.year] ?? 0];
  const n = Math.max(0, ...vals);
  return n >= 4 ? "leaving" : n >= 2 ? "drifting" : "stable";
}

export const YEAR_LEGEND = { stable: "0–1 months outside normal", drifting: "2–3 months", leaving: "4+ months", no_data: "No data" };
