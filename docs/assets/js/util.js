// Shared formatting + colour helpers.

export const STATUS = {
  stable: { label: "Still Mars-like", color: "var(--stable)", hex: "#3fb68b" },
  drifting: { label: "Drifting", color: "var(--drifting)", hex: "#e8b04a" },
  leaving: { label: "Leaving Mars-like conditions", color: "var(--leaving)", hex: "#e5534b" },
  no_data: { label: "No data yet", color: "var(--no-data)", hex: "#6b7385" },
};

export function statusFor(site, variable, driftChange) {
  if (variable === "all") return site.status;
  const m = site.metrics[variable];
  if (!m || m.change == null) return "no_data";
  if (m.change >= driftChange * 2) return "leaving";
  if (m.change >= driftChange) return "drifting";
  return "stable";
}

export const fmt = (x, digits = 1) => (x == null ? "–" : Number(x).toFixed(digits));

export function fmtChange(x) {
  if (x == null) return '<span class="muted">–</span>';
  const cls = x > 0 ? "up" : x < 0 ? "down" : "";
  return `<span class="${cls}">${x > 0 ? "+" : ""}${Number(x).toFixed(1)}</span>`;
}

export function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

export function meanChange(site) {
  const vals = Object.values(site.metrics).map((m) => m.change).filter((v) => v != null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
}
