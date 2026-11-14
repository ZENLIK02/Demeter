// World map: one dot per site, coloured by status (or by one variable). Click = select site.
/* global L */

import { STATUS, statusFor, escapeHtml } from "../util.js";
import { yearStatus, YEAR_LEGEND } from "./year-slider.js";

export function mount(el, { subscribe, setState }) {
  const map = L.map(el, { worldCopyJump: true, minZoom: 1, attributionControl: true }).setView([25, 0], 1.6);
  // NASA GIBS Blue Marble: open, no API key (https://nasa-gibs.github.io/gibs-api-docs/)
  L.tileLayer("https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief_Bathymetry/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg", {
    attribution: 'Imagery: <a href="https://earthdata.nasa.gov/gibs">NASA GIBS</a> Blue Marble',
    maxZoom: 8,
    opacity: 0.75,
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
      const byYear = s.year != null && s.yearCounts;
      const status = STATUS[byYear ? yearStatus(site, s) : statusFor(site, s.variable, drift)];
      const selected = site.id === s.selectedSiteId;
      m.setStyle({ color: selected ? "#ffffff" : status.hex, fillColor: status.hex });
      m.setRadius(selected ? 11 : 8);
      if (selected) m.bringToFront();
    }
    if (legend) {
      legend.innerHTML = Object.entries(STATUS)
        .map(([key, st]) => `<span><i style="background:${st.hex}"></i>${s.year != null ? YEAR_LEGEND[key] : st.label}</span>`)
        .join("");
    }
  }

  subscribe((s) => {
    if (s.summary) draw(s);
  });
  // Leaflet needs a size recalculation if the container was laid out after init.
  setTimeout(() => map.invalidateSize(), 0);
}
