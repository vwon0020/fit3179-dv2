const THEME = {
  background: null,
  font: "IBM Plex Sans",
  padding: 4,
  view: { stroke: null },
  axis: {
    labelFont: "IBM Plex Sans",
    titleFont: "IBM Plex Sans",
    labelColor: "#5b6470",
    titleColor: "#3b4148",
    labelFontSize: 11.5,
    titleFontSize: 12,
    titleFontWeight: 600,
    gridColor: "#ebe7de",
    domainColor: "#b9b3a6",
    tickColor: "#b9b3a6"
  },
  legend: {
    labelFont: "IBM Plex Sans",
    titleFont: "IBM Plex Sans",
    labelColor: "#3b4148",
    titleColor: "#1b1f24",
    labelFontSize: 12,
    titleFontSize: 12,
    titleFontWeight: 600,
    titleLimit: 320
  },
  header: {
    labelFont: "Space Grotesk",
    titleFont: "Space Grotesk"
  },
  title: {
    font: "Space Grotesk",
    subtitleFont: "IBM Plex Sans",
    color: "#1b1f24",
    subtitleColor: "#5b6470",
    anchor: "start"
  },
  text: { font: "IBM Plex Sans", color: "#1b1f24" },
  mark: { font: "IBM Plex Sans" }
};

const embedOptions = {
  actions: false,
  renderer: "svg",
  config: THEME,
  tooltip: { theme: "custom" }
};

async function embedAll() {
  const slots = document.querySelectorAll("[data-spec]");
  const jobs = [...slots].map((el) =>
    vegaEmbed(el, el.dataset.spec, embedOptions).catch((err) => {
      console.error("Chart failed:", el.dataset.spec, err);
      el.innerHTML = '<p class="chart-error">This chart could not be loaded.</p>';
    })
  );
  await Promise.all(jobs);
  document.body.classList.add("charts-ready");
}

// Wait for the web fonts so Vega measures label widths with the right typeface.
(document.fonts ? document.fonts.ready : Promise.resolve()).then(embedAll);
