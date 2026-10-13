
import json, re, math, csv, sys
import pandas as pd

RAW = sys.argv[1]
OUT = sys.argv[2]

# ISO lookup
iso = pd.read_csv(f"{RAW}/iso.csv", keep_default_na=False, dtype=str)
iso2_to = {r["alpha-2"]: r for _, r in iso.iterrows()}

# World Bank
wb = json.load(open(f"{RAW}/wb.json"))
def wbmap(ind):
    return {r[0]: (r[3], r[2]) for r in wb[ind] if r[3] is not None}
gdp, pop, subs, subs100, net = (wbmap(k) for k in
    ["NY.GDP.PCAP.CD", "SP.POP.TOTL", "IT.CEL.SETS", "IT.CEL.SETS.P2", "IT.NET.USER.ZS"])

# TopoJSON centroids (largest polygon, planar lon/lat)
topo = json.load(open(f"{RAW}/countries-110m.json"))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
def ring(idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts
def area_centroid(pts):
    A = cx = cy = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        c = x0 * y1 - x1 * y0
        A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    if A == 0: return 0, pts[0]
    return abs(A / 2), (cx / (3 * A), cy / (3 * A))
cent = {}
for g in topo["objects"]["countries"]["geometries"]:
    if "id" not in g: continue
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    best = max((area_centroid(ring(p[0])) for p in polys), key=lambda t: t[0])
    cent[g["id"]] = best[1]
# hand-corrections where the largest-polygon centroid falls awkwardly (lon, lat)
cent["840"] = (-98.5, 39.5)   # USA mainland
cent["643"] = (96.0, 61.0)    # Russia
cent["124"] = (-106.0, 57.0)  # Canada
cent["250"] = (2.4, 46.6)     # France (metropolitan)

# StatCounter: phone brand share by country, Oct 2025 - Sep 2026 average
raw_world = json.load(open(f"{RAW}/world_raw.json"))
def parse_sc(text):
    rows = list(csv.reader(text.strip().splitlines()))
    hdr = rows[0]
    return [dict(zip(hdr, [r[0]] + [float(v) for v in r[1:]])) for r in rows[1:] if len(r) == len(hdr)]

CHINESE = ["Xiaomi", "Oppo", "Vivo", "Huawei", "Honor", "Realme", "OnePlus", "ZTE", "Meizu", "Lenovo", "TCL"]
TRANSSION = ["Tecno", "Infinix", "Itel"]
LEADERS = ["Apple", "Samsung", "Xiaomi", "Tecno", "Vivo", "Oppo", "Infinix"]
NAMES = {"KR": "South Korea", "KP": "North Korea", "CD": "DR Congo", "CG": "Congo", "GB": "United Kingdom",
         "US": "United States", "RU": "Russia", "VN": "Vietnam", "TW": "Taiwan", "LA": "Laos", "SY": "Syria",
         "MD": "Moldova", "MK": "North Macedonia", "CZ": "Czechia", "TZ": "Tanzania", "BO": "Bolivia",
         "VE": "Venezuela", "IR": "Iran", "PS": "Palestine", "FM": "Micronesia", "SZ": "Eswatini",
         "CI": "Côte d'Ivoire", "TR": "Türkiye", "AE": "United Arab Emirates", "DO": "Dominican Republic"}
world = []
for iso2, text in raw_world.items():
    rows = parse_sc(text)
    if not rows or iso2 not in iso2_to: continue
    brands = [k for k in rows[0] if k != "Date"]
    avg = {b: sum(r[b] for r in rows) / len(rows) for b in brands}
    named = sorted(((b, v) for b, v in avg.items() if b not in ("Unknown", "Other")), key=lambda t: -t[1])
    if not named or named[0][1] < 10: continue   # too little traffic to be meaningful
    r = iso2_to[iso2]; n3 = r["country-code"]; i3 = r["alpha-3"]
    lon, lat = cent.get(n3, (None, None))
    world.append({
        "id": n3, "iso2": iso2, "iso3": i3,
        "country": NAMES.get(iso2, r["name"].split(",")[0].split(" (")[0]),
        "region": r["region"], "subregion": r["sub-region"],
        "leader": named[0][0] if named[0][0] in LEADERS else "Other brand",
        "leaderRaw": named[0][0], "leaderShare": round(named[0][1], 1),
        "second": named[1][0], "secondShare": round(named[1][1], 1),
        "apple": round(avg.get("Apple", 0), 1), "samsung": round(avg.get("Samsung", 0), 1),
        "chinese": round(sum(avg.get(b, 0) for b in CHINESE), 1),
        "transsion": round(sum(avg.get(b, 0) for b in TRANSSION), 1),
        "gdpPc": round(gdp[i3][0]) if i3 in gdp else None, "gdpYear": gdp[i3][1] if i3 in gdp else None,
        "pop": pop[i3][0] if i3 in pop else None,
        "subs": subs[i3][0] if i3 in subs else None, "subsYear": subs[i3][1] if i3 in subs else None,
        "subsPer100": round(subs100[i3][0], 1) if i3 in subs100 else None,
        "internetPct": round(net[i3][0], 1) if i3 in net else None,
        "lon": round(lon, 2) if lon is not None else None, "lat": round(lat, 2) if lat is not None else None,
    })
    w = world[-1]
    groups = {"Apple": w["apple"], "Samsung": w["samsung"], "Chinese brands": w["chinese"], "Transsion (Tecno, Infinix, itel)": w["transsion"]}
    w["bigGroup"] = max(groups, key=groups.get)
json.dump(world, open(f"{OUT}/world_phones.json", "w"), indent=1)
print("countries:", len(world))

# StatCounter monthly brand share: Australia + Worldwide (long format)
KEEP = ["Apple", "Samsung", "Google", "Oppo", "Motorola", "Huawei", "Xiaomi", "HTC", "Sony", "Nokia", "LG", "Vivo"]
long = []
for region, f in [("Australia", "au_vendor.csv"), ("World", "ww_vendor.csv")]:
    for r in parse_sc(open(f"{RAW}/{f}").read()):
        other = 100.0
        for b in KEEP:
            v = r.get(b, 0.0); other -= v
            long.append({"date": r["Date"], "region": region, "brand": b, "share": round(v, 2)})
        long.append({"date": r["Date"], "region": region, "brand": "Other", "share": round(max(other, 0), 2)})
pd.DataFrame(long).to_csv(f"{OUT}/brand_share_monthly.csv", index=False)

# StatCounter: platform (desktop / mobile / tablet), Australia
plat = pd.DataFrame(parse_sc(open(f"{RAW}/au_platform.csv").read()))
plat.to_csv(f"{OUT}/au_platform_monthly.csv", index=False)

# StatCounter: desktop OS, Australia
os_ = pd.DataFrame(parse_sc(open(f"{RAW}/au_desktop_os.csv").read()))
os_["macOS"] = os_["OS X"] + os_["macOS"]
os_["Other"] = 100 - os_["Windows"] - os_["macOS"] - os_["Chrome OS"] - os_["Linux"]
os_ = os_[["Date", "Windows", "macOS", "Chrome OS", "Linux", "Other"]].round(2)
os_.melt("Date", var_name="os", value_name="share").rename(columns={"Date": "date"}).to_csv(f"{OUT}/au_desktop_os_monthly.csv", index=False)

# StatCounter: tablet vendor, Australia
tab = pd.DataFrame(parse_sc(open(f"{RAW}/au_tablet_vendor.csv").read()))
tkeep = ["Apple", "Samsung", "Lenovo", "Microsoft", "Amazon", "Google"]
tab["Other"] = 100 - tab[tkeep].sum(axis=1)
tab[["Date"] + tkeep + ["Other"]].round(2).melt("Date", var_name="brand", value_name="share").rename(columns={"Date": "date"}).to_csv(f"{OUT}/au_tablet_monthly.csv", index=False)

# Mobiles Dataset (2025): phone specifications
m = pd.read_csv(f"{RAW}/mobiles.csv", encoding="latin1")
def num(s):
    """First number in a text field, e.g. '3,600mAh' -> 3600, '48MP + 12MP' -> 48."""
    mt = re.search(r"\d+(?:\.\d+)?", str(s).replace(",", ""))
    return float(mt.group()) if mt else float("nan")
brand_fix = {"POCO": "Xiaomi", "Poco": "Xiaomi", "iQOO": "Vivo"}
ph = pd.DataFrame({
    "brand": m["Company Name"].replace(brand_fix),
    "model": m["Model Name"].str.strip(),
    "year": m["Launched Year"],
    "weight_g": m["Mobile Weight"].map(num),
    "ram_gb": m["RAM"].map(num),
    "front_mp": m["Front Camera"].map(num),
    "main_mp": m["Back Camera"].map(num),
    "battery_mah": m["Battery Capacity"].map(num),
    "screen_in": m["Screen Size"].map(num),
    "price_usd": m["Launched Price (USA)"].map(num),
})
ph = ph[(ph.screen_in <= 7.0) & ph.price_usd.between(50, 3000) & ph.year.between(2019, 2025)]
ph = ph.drop_duplicates(["brand", "model"])
ph.to_csv(f"{OUT}/phones_specs.csv", index=False)
print("phones:", len(ph), ph.brand.value_counts().to_dict())
