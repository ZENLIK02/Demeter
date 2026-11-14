// One time-series chart: monthly values, the site's own threshold, excursion months in red,
// baseline / recent periods shaded, documented events labelled.
/* global Chart */

const annotationPlugin = window["chartjs-plugin-annotation"];
if (annotationPlugin) Chart.register(annotationPlugin);

const COLORS = { line: "#9aa3b5", threshold: "#e8b04a", excursion: "#e5534b", grid: "#2a3142", text: "#9aa3b5" };

/**
 * @param {HTMLCanvasElement} canvas
 * @param {object} series   one entry of series/<site>.json `variables`
 * @param {object} opts     { method, events } - method from sites.json, events for this variable
 * @returns {Chart}
 */
export function renderChart(canvas, series, { method, events = [] }) {
  const { dates, values, threshold, excursion } = series;
  const first = (y) => `${y}-01`;
  const last = (y) => `${y}-12`;

  const annotations = {
    baseline: box(first(method.baseline[0]), last(method.baseline[1]), "rgba(63,182,139,0.07)", "baseline"),
    recent: box(first(method.recent[0]), last(method.recent[1]), "rgba(226,112,58,0.08)", "recent"),
  };
  events.forEach((e, i) => {
    annotations[`event${i}`] = {
      type: "box",
      xMin: e.start,
      xMax: e.end,
      backgroundColor: "rgba(229,83,75,0.12)",
      borderColor: "rgba(229,83,75,0.6)",
      borderWidth: 1,
      label: { display: true, content: e.label, position: { x: "center", y: "start" }, color: "#e8eaf0", font: { size: 10 } },
    };
  });

  return new Chart(canvas, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        { label: `Monthly value (${series.unit})`, data: values, borderColor: COLORS.line, borderWidth: 1, pointRadius: 0, tension: 0 },
        { label: "Threshold (site's own baseline)", data: threshold, borderColor: COLORS.threshold, borderWidth: 1, borderDash: [4, 3], pointRadius: 0 },
        {
          label: "Excursion month",
          data: values.map((v, i) => (excursion[i] ? v : null)),
          showLine: false,
          pointRadius: 3,
          pointBackgroundColor: COLORS.excursion,
          pointBorderColor: COLORS.excursion,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        annotation: { annotations },
        tooltip: { filter: (item) => item.datasetIndex !== 2 },
      },
      scales: {
        x: {
          ticks: { color: COLORS.text, maxRotation: 0, autoSkip: false, callback(v) { const d = this.getLabelForValue(v); return d.endsWith("-01") && Number(d.slice(0, 4)) % 5 === 0 ? d.slice(0, 4) : null; } },
          grid: { display: false },
        },
        y: { ticks: { color: COLORS.text, maxTicksLimit: 5 }, grid: { color: COLORS.grid } },
      },
    },
  });
}

function box(xMin, xMax, backgroundColor, text) {
  return {
    type: "box",
    xMin,
    xMax,
    backgroundColor,
    borderWidth: 0,
    label: { display: true, content: text, position: { x: "start", y: "end" }, color: "#6b7385", font: { size: 9 } },
  };
}
