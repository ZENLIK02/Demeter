// Site detail panel: verdict, evidence, decade comparison, one chart per variable.
// All strings from data files go through escapeHtml before reaching innerHTML.

import { loadSeries } from "../data.js";
import { STATUS, fmt, fmtChange, escapeHtml } from "../util.js";
import { renderChart } from "./chart.js";

export function mount(el, { subscribe }) {
  let charts = [];
  let token = 0; // guards against a slow series load overwriting a newer selection

  function empty() {
    el.innerHTML = '<div class="empty"><p>Select a site on the map<br>to see how often it leaves Mars-like conditions.</p></div>';
  }

  async function show(s) {
    const site = s.summary.sites.find((x) => x.id === s.selectedSiteId);
    if (!site) return empty();
    const my = ++token;
    const { method, variables } = s.summary;
    const st = STATUS[site.status];

    const rows = variables
      .filter((v) => site.metrics[v.id])
      .map((v) => {
        const m = site.metrics[v.id];
        return `<tr><td>${escapeHtml(v.label)}</td><td>${fmt(m.rate_baseline)}</td><td>${fmt(m.rate_recent)}</td><td>${fmtChange(m.change)}</td></tr>`;
      })
      .join("");

    const events = (site.events || [])
      .map((e) => {
        const cite = e.url ? `<a href="${escapeHtml(e.url)}" target="_blank" rel="noopener">${escapeHtml(e.citation)}</a>` : escapeHtml(e.citation);
        return `<div class="event"><strong>${escapeHtml(e.label)}</strong> (${escapeHtml(e.start)} to ${escapeHtml(e.end)})<br>${cite}</div>`;
      })
      .join("");

    el.innerHTML = `
      <h2>${escapeHtml(site.name)}</h2>
      <p class="sub">${escapeHtml(site.country)} · ${escapeHtml(site.analog_for)}${site.polar ? " · polar site" : ""}</p>
      <span class="badge ${site.status}">${st.label}</span>
      <p class="verdict">${escapeHtml(verdict(site, variables, method))}</p>
      ${events}
      <table class="metrics">
        <thead><tr><th>Excursion months / year</th><th>${method.baseline[0]}–${method.baseline[1]}</th><th>${method.recent[0]}–${method.recent[1]}</th><th>Change</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div id="panel-charts"><p class="muted">Loading monthly record…</p></div>`;

    let series;
    try {
      series = await loadSeries(site.id);
    } catch (err) {
      if (my === token) el.querySelector("#panel-charts").innerHTML = `<p class="muted">Could not load series (${escapeHtml(err.message)})</p>`;
      return;
    }
    if (my !== token) return;

    charts.forEach((c) => c.destroy());
    charts = [];
    const holder = el.querySelector("#panel-charts");
    holder.innerHTML = "";
    for (const v of variables) {
      const data = series.variables[v.id];
      if (!data) continue;
      const block = document.createElement("div");
      block.className = "chart-block";
      block.innerHTML = `<h3>${escapeHtml(v.label)} <span class="muted">(${escapeHtml(v.unit)})</span></h3>
        <div class="chart-box"><canvas></canvas></div>
        <p class="note">${escapeHtml(v.why)} Red dots: months above the site's own ${method.baseline[0]}–${method.baseline[1]} threshold. Source: ${escapeHtml(data.source)}.</p>`;
      holder.appendChild(block);
      const eventsForVar = (site.events || []).filter((e) => e.variable === v.id);
      charts.push(renderChart(block.querySelector("canvas"), data, { method, events: eventsForVar }));
    }
  }

  subscribe((s, patch) => {
    if (!s.summary) return;
    if ("summary" in patch || "selectedSiteId" in patch) show(s);
  });
  empty();
}

function verdict(site, variables, method) {
  const drifting = variables.filter((v) => site.metrics[v.id]?.drifting).map((v) => v.label.toLowerCase());
  if (site.status === "no_data") return "Not enough data to compare decades.";
  if (!drifting.length) return `No variable left its ${method.baseline[0]}–${method.baseline[1]} range more often in ${method.recent[0]}–${method.recent[1]}.`;
  return `More frequent excursions in ${method.recent[0]}–${method.recent[1]} than in ${method.baseline[0]}–${method.baseline[1]} for: ${drifting.join(", ")}.`;
}
