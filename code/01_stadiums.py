"""Step 1: venues. Aggregate the Wikidata rows (one per combination of values) to one record per venue: the largest
capacity recorded, every place it is located in with that place's largest recorded population, its tenants; the town is
the smallest populated place it is located in. Classify the kind of venue (racecourse, motor circuit, winter sports,
bullring...) and guess the sport from the name and tenants. For UK venues also find the nearest town, city or village in
the Wikidata settlement list within 4 km. Writes WORK/venues.pkl."""
import numpy as np, pandas as pd
from collections import defaultdict
from common import *

C = {}
for f in jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]:
    p = f["properties"]
    C[p["WIKIDATAID"]] = (p["ISO_A2_EH"], p["NAME"], p["CONTINENT"], p["POP_EST"])

V = {}
LOC = defaultdict(lambda: {"label": "", "pop": []})
for r in read_tsv(STADIUMS):
    s = qid(r["s"])
    d = V.setdefault(s, {"qid": s, "name": "", "caps": set(), "coords": set(), "ctry": set(), "locs": set(), "occ": {}, "sl": 0})
    if r["sn"]: d["name"] = r["sn"]
    if r["cap"]:
        try: d["caps"].add(float(r["cap"]))
        except ValueError: pass
    x, y = point(r["coord"])
    if x is not None: d["coords"].add((round(x, 5), round(y, 5)))
    if r["ctry"]: d["ctry"].add(qid(r["ctry"]))
    if r["loc"]:
        l = qid(r["loc"]); d["locs"].add(l)
        if r["locl"]: LOC[l]["label"] = r["locl"]
        if r["pop"]:
            try: LOC[l]["pop"].append(float(r["pop"]))
            except ValueError: pass
    if r["occ"]: d["occ"][qid(r["occ"])] = r["occl"]
    if r["sl"]: d["sl"] = max(d["sl"], int(float(r["sl"])))

KIND = [("horse", r"racecourse(?! ground)|race course|hippodrom|hip[oó]dromo|ippodromo|(?<!rad)rennbahn|galopprenn|trabrenn|racetrack|turf club|jockey club"),
        ("motor", r"speedway|raceway|circuit\b|aut[oó]dromo|autodrom|motodrom|dragway|motor racing|motorsport|\bring$|-ring$|superspeedway"),
        ("winter", r"\bski\b|\bski stadium|biathlon|ski jump|jumping|schanze|cross-country|skating|eisstadion|\bice stadium|ghiaccio|bobsleigh|luge|snow harp"),
        ("bullring", r"plaza de toros|bullring|pra[cç]a de touros|ar[eè]nes|arena de toros"),
        ("show", r"showground|equestrian|rodeo|fairground|exhibition"),
        ("tennis", r"tennis"),
        ("water", r"waterway|regatta|rowing|canoe|aquatic|swimming|natatorium")]
SPORT = [("gaelic", r"\bgaa\b|gaelic|hurling|camogie"), ("cricket", r"cricket"), ("american", r"football team|\bfootball\b(?!.*club)|bowl\b|nfl|ncaa|new york (giants|jets)|patriots|buffalo bills|detroit lions"),
         ("rugby", r"rugby|\brlfc\b|\brfc\b|\brl\b|rugby league|super league"), ("aussie", r"football club|\bafl\b|\bsanfl\b|\bwafl\b"),
         ("baseball", r"baseball|ballpark|\bsox\b|yankees|dodgers"),
         ("hockey", r"hockey|\bhc\b|\bhk\b|ice|eishockey"), ("basketball", r"basketball|basket|\bbc\b|\bkings\b|36ers"),
         ("soccer", r"\bf\.?c\.?\b|\bs\.?c\.?\b|football club|fútbol|futbol|calcio|fußball|\bsk\b|\bif\b|\bfk\b|\bnk\b|united|athletic|city|\bcf\b|\bcd\b|\bud\b|\bsv\b|\bvfb\b|\bvfl\b|\bks\b|\bafc\b|national football|national soccer|men's national|women's national|soccer")]
rows = []
for s, d in V.items():
    if not d["caps"] or not d["coords"]: continue
    cs = np.array(sorted(d["coords"]))
    ct = sorted(d["ctry"])
    iso, cname, cont, cpop = C.get(ct[0], ("", "", "", np.nan)) if ct else ("", "", "", np.nan)
    locs = [(l, LOC[l]["label"], max(LOC[l]["pop"]) if LOC[l]["pop"] else np.nan) for l in sorted(d["locs"])]
    popd = [x for x in locs if x[2] == x[2] and x[2] > 0]
    town = min(popd, key=lambda x: x[2]) if popd else (locs[0] if locs else ("", "", np.nan))
    occ = "; ".join(sorted(set(d["occ"].values()))[:6])
    text = (d["name"] + " " + occ).lower()
    kind = next((k for k, rx in KIND if re.search(rx, d["name"].lower())), "ground")
    if kind == "ground" and re.search(r"\barena\b|dome|hall|centre|center|palasport|halle|dvorana|coliseum|garden", d["name"].lower()) and not re.search(r"stadium|stadion|stade|estadio|est[aá]dio|stadio|park|field|ground|oval", d["name"].lower()):
        kind = "arena"
    sport = next((k for k, rx in SPORT if re.search(rx, text)), "")
    if sport == "american" and iso not in ("US", "CA"): sport = "soccer" if re.search(r"football", text) else ""
    if sport == "aussie" and iso != "AU": sport = "soccer"
    if sport in ("baseball",) and iso not in ("US", "JP", "KR", "TW", "CU", "DO", "MX", "VE", "PR", "NI", "PA", "CA", "AU") and "baseball" not in text and "ballpark" not in text: sport = ""
    rows.append(dict(qid=s, name=d["name"] or (f"Ground of {sorted(d['occ'].values())[0]}" if d["occ"] else f"Unnamed ground ({s})"), cap=max(d["caps"]), cap_min=min(d["caps"]), n_caps=len(d["caps"]), lon=float(np.median(cs[:, 0])), lat=float(np.median(cs[:, 1])),
                     iso=iso, country=cname, continent=cont, country_pop=cpop, ctry_qid=ct[0] if ct else "", n_locs=len(locs),
                     loc=town[0], loc_label=town[1], pop=town[2], all_locs="; ".join(f"{l} {lab} {p:.0f}" if p == p else f"{l} {lab}" for l, lab, p in locs),
                     tenants=occ, sitelinks=d["sl"], kind=kind, sport=sport))
VV = pd.DataFrame(rows)

# ---- UK: the nearest town, city or village within 4 km
TOWN_TYPES = {"town", "market town", "city", "big city", "county town", "cathedral city", "Village", "large village", "new town (UK)",
              "town of the United Kingdom", "city of United Kingdom", "city status in the United Kingdom", "seaside resort", "small town", "port city", "spa town"}
ST = defaultdict(lambda: {"label": "", "types": set(), "coords": set(), "pop": []})
for r in read_tsv(SETTLE):
    t = ST[qid(r["p"])]
    t["label"] = r["pl"]; t["types"].add(r["typel"])
    x, y = point(r["coord"])
    if x is not None: t["coords"].add((x, y))
    if r["pop"]:
        try: t["pop"].append(float(r["pop"]))
        except ValueError: pass
SE = pd.DataFrame([dict(sq=q, sname=t["label"], slon=x, slat=y, spop=max(t["pop"]) if t["pop"] else np.nan, stype="; ".join(sorted(t["types"] & TOWN_TYPES)))
                   for q, t in ST.items() if t["types"] & TOWN_TYPES for x, y in t["coords"]])
SE = SE[SE.spop.notna()]
uk = VV.iso == "GB"
for c in ("uk_town", "uk_town_qid", "uk_town_pop", "uk_town_km"):
    VV[c] = np.nan if c.endswith(("pop", "km")) else ""
for i in VV.index[uk]:
    d = km(VV.at[i, "lat"], VV.at[i, "lon"], SE.slat.values, SE.slon.values)
    j = int(np.argmin(d))
    if d[j] <= 4:
        VV.loc[i, ["uk_town", "uk_town_qid", "uk_town_pop", "uk_town_km"]] = [SE.sname.iloc[j], SE.sq.iloc[j], SE.spop.iloc[j], float(d[j])]
print("venues", len(VV), "with a population", VV["pop"].notna().sum(), "UK", int(uk.sum()), "UK with a town", VV.uk_town_pop.notna().sum())
print(VV.kind.value_counts().to_dict()); print(VV.sport.value_counts().to_dict())
VV.to_pickle(f"{WORK}/venues.pkl")
