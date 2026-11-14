// "Colour sites by" pills: overall status, or one variable.

export function mount(el, { subscribe, setState }) {
  el.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-var]");
    if (btn) setState({ variable: btn.dataset.var });
  });

  subscribe((s, patch) => {
    if (!s.summary || !("summary" in patch || "variable" in patch)) return;
    const options = [{ id: "all", label: "Overall" }, ...s.summary.variables];
    el.innerHTML = options
      .map((o) => `<button type="button" data-var="${o.id}" aria-pressed="${o.id === s.variable}">${o.label}</button>`)
      .join("");
  });
}
