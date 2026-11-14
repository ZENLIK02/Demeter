// Headline stats strip. Component contract: export mount(el, store).

export function mount(el, { subscribe }) {
  subscribe((s, patch) => {
    if (!("summary" in patch) || !s.summary) return;
    const { headline: h, method: m, variables } = s.summary;
    el.innerHTML = `
      <div class="stat primary">
        <div class="value">${h.sites_drifting} of ${h.sites_total}</div>
        <div class="label">sites leave Mars-like conditions more often in ${m.recent[0]}–${m.recent[1]} than in ${m.baseline[0]}–${m.baseline[1]}</div>
      </div>
      <div class="stat">
        <div class="value">${h.sites_leaving}</div>
        <div class="label">sites drifting on half or more of the variables tracked</div>
      </div>
      <div class="stat">
        <div class="value">${variables.length}</div>
        <div class="label">NASA variables: ${variables.map((v) => v.label).join(", ")}</div>
      </div>
      <div class="stat">
        <div class="value">${m.baseline[0]}–${m.recent[1]}</div>
        <div class="label">monthly record, each site compared with its own ${m.baseline[0]}–${m.baseline[1]} normal</div>
      </div>`;
  });
}
