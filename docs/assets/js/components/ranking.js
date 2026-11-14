// Ranking table: sites sorted by average change in excursion months per year. Click a row = select.

import { STATUS, fmtChange, escapeHtml, meanChange } from "../util.js";

export function mount(el, { subscribe, setState }) {
  el.addEventListener("click", (e) => {
    const row = e.target.closest("tr[data-site]");
    if (row) setState({ selectedSiteId: row.dataset.site });
  });

  subscribe((s, patch) => {
    if (!s.summary || !("summary" in patch || "selectedSiteId" in patch)) return;
    const { variables, sites } = s.summary;
    const sorted = [...sites].sort((a, b) => (meanChange(b) ?? -Infinity) - (meanChange(a) ?? -Infinity));
    const head = `<tr><th>Site</th><th>Country</th><th>Status</th>${variables.map((v) => `<th>${escapeHtml(v.label)}</th>`).join("")}<th>Average change</th></tr>`;
    const body = sorted
      .map((site) => {
        const cells = variables.map((v) => `<td>${fmtChange(site.metrics[v.id]?.change)}</td>`).join("");
        return `<tr data-site="${escapeHtml(site.id)}" aria-selected="${site.id === s.selectedSiteId}">
          <td>${escapeHtml(site.name)}</td><td>${escapeHtml(site.country)}</td>
          <td><span class="badge ${site.status}">${STATUS[site.status].label}</span></td>${cells}<td>${fmtChange(meanChange(site))}</td></tr>`;
      })
      .join("");
    el.innerHTML = `<table class="ranking"><thead>${head}</thead><tbody>${body}</tbody></table>`;
  });
}
