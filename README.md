# Who's in Your Pocket?

**FIT3179 Data Visualisation 2: Consumer Electronics (Topic 12)**
Vanessa Wong · Monash University · October 2026

A scrolling data story about the phones, tablets and computers Australians use, compared with the rest of the world. All charts and maps are built with [Vega-Lite 5](https://vega.github.io/vega-lite/).

**Live page:** `https://<your-github-username>.github.io/<repo-name>/`

## Repository layout

| Folder | Contents |
|---|---|
| `index.html` | The web page (single scrolling page) |
| `specs/` | One human-readable Vega-Lite JSON specification per chart or map (12 files) |
| `data/` | The data files the charts load (about 0.5 MB in total) |
| `prep/prep.py` | The script that reshaped the raw downloads into `data/` (joins and unit parsing only; values are unchanged) |
| `css/`, `js/` | Page styling and the embedding script with the shared chart theme |
| `lib/` | Vega 5.30, Vega-Lite 5.21 and Vega-Embed 6.26 (BSD-3 licence) |
| `fonts/` | Space Grotesk and IBM Plex (SIL Open Font License) |
| `sketch/` | PDF of the hand-drawn design sketch |

## Charts

| # | Idiom | Spec |
|---|---|---|
| Map 1 | Categorical choropleth (Equal Earth) | `specs/01_map_leader.vl.json` |
| Map 2 | Bivariate choropleth + interactive 3×3 key | `specs/02_map_bivariate.vl.json` |
| Map 3 | Proportional symbol map | `specs/03_map_symbols.vl.json` |
| 4 | Waffle (unit) chart, small multiples, custom phone glyph | `specs/04_waffle_au_world.vl.json` |
| 5 | Ridgeline plot | `specs/05_ridgeline_au.vl.json` |
| 6 | Bump chart | `specs/06_bump_au.vl.json` |
| 7 | Calendar heatmap (diverging) | `specs/07_heatmap_platform.vl.json` |
| 8 | Multi-line chart | `specs/08_line_desktop_os.vl.json` |
| 9 | 100% stacked bar chart | `specs/09_bar_tablets.vl.json` |
| 10 | Box plot | `specs/10_boxplot_price.vl.json` |
| 11 | Violin plot (density) | `specs/11_violin_battery.vl.json` |
| 12 | Parallel coordinates | `specs/12_parallel_specs.vl.json` |

## Data sources

1. **StatCounter Global Stats**: mobile vendor, tablet vendor, desktop OS and platform market share (CC BY-SA 3.0). https://gs.statcounter.com
2. **World Bank WDI**: GDP per capita, population, mobile cellular subscriptions (ITU) (CC BY 4.0). https://data.worldbank.org
3. **Mobiles Dataset (2025)** by Kaggle user abdulmalik1518. https://www.kaggle.com/datasets/abdulmalik1518/mobiles-dataset-2025
4. **world-atlas** 110m TopoJSON (Natural Earth). https://github.com/topojson/world-atlas
5. **ISO-3166 country codes**. https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes

## Run locally

The page loads its specs and data with `fetch`, so open it through a local web server rather than by double-clicking:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## AI acknowledgement

Generative AI (Claude, Anthropic) was used to help collect and prepare the data, write the Vega-Lite code and page layout, and edit the text. All data comes from the cited sources and was not altered.
