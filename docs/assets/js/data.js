// The only module that knows file paths. Shapes are defined in contracts/*.schema.json.

const cache = new Map();

async function getJSON(url) {
  if (!cache.has(url)) {
    cache.set(
      url,
      fetch(url).then((r) => {
        if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
        return r.json();
      }),
    );
  }
  return cache.get(url);
}

export const loadSummary = () => getJSON("data/sites.json");
export const loadSeries = (siteId) => getJSON(`data/series/${encodeURIComponent(siteId)}.json`);
