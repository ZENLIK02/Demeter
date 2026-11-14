// World map: one dot per site, coloured by status (or by one variable). Click = select site.
/* global L */

import { STATUS, statusFor, escapeHtml } from "../util.js";

export function mount(el, { subscribe, setState }) {
  const map = L.map(el, { worldCopyJump: true, minZoom: 1, attributionControl: true }).setView([25, 0], 1.6);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 8,
  }).addTo(map);

  const markers = new Map(); // site id -> circleMarker
  const legend = document.getElementById("legend");

  function draw(s) {
    const drift = s.summary.method.drift_change_months_per_year;
    for (const site of s.summary.sites) {
      let m = markers.get(site.id);
      if (!m) {
        m = L.circleMarker([site.lat, site.lon], { weight: 2, fillOpacity: 0.85 }).addTo(map);
        m.bindTooltip(escapeHtml(site.name), { direction: "top" });
        m.on("click", () => setState({ selectedSiteId: site.id }));
        markers.set(site.id, m);
      }
      const status = STATUS[statusFor(site, s.variable, drift)];
      const selected = site.id === s.selectedSiteId;
      m.setStyle({ color: selected ? "#ffffff" : status.hex, fillColor: status.hex });
      m.setRadius(selected ? 11 : 8);
      if (selected) m.bringToFront();
    }
    if (legend) {
      legend.innerHTML = Object.values(STATUS)
        .map((st) => `<span><i style="background:${st.hex}"></i>${st.label}</span>`)
        .join("");
    }
  }

  subscribe((s) => {
    if (s.summary) draw(s);
  });
  // Leaflet needs a size recalculation if the container was laid out after init.
  setTimeout(() => map.invalidateSize(), 0);
}
