"""Step 2: apply code/overrides.csv, compute capacity / town population, rank, and write data/*.csv, data/map.json and
data/results.json (every number quoted anywhere comes from results.json)."""
import numpy as np, pandas as pd
from common import *

V = pd.read_pickle(f"{WORK}/venues.pkl")
O = pd.read_csv(os.path.join(ROOT, "code", "overrides.csv"), keep_default_na=False)
assert O.qid.is_unique and set(O.verdict) <= {"ok", "district", "wrong", "region", "unsure"}
assert set(O.qid) <= set(V.qid), set(O.qid) - set(V.qid)
V = V.merge(O[["qid", "verdict", "reason", "cap_fix", "pop_fix", "town_fix", "name_fix", "fix_source"]], on="qid", how="left")
V["verdict"] = V.verdict.fillna("unreviewed")
for c in ("reason", "cap_fix", "pop_fix", "town_fix", "name_fix", "fix_source"):
    V[c] = V[c].fillna("")
# The first pass uses Wikidata's figures as they stand (largest recorded capacity and population)
V["cap_raw"], V["pop_raw"] = V.cap, V["pop"]
V["ratio_raw"] = np.where(V.pop_raw > 0, V.cap_raw / V.pop_raw, np.nan)
# Hand checks (code/overrides.csv): current capacities and populations for the cases a reader will quote, and 2022 census
# populations for Irish towns that Wikidata lacks or gives only from an older census; every one has a source in fix_source
fx = V.cap_fix.ne("")
V.loc[fx, "cap"] = V.loc[fx, "cap_fix"].astype(float)
fx = V.pop_fix.ne("")
V.loc[fx, "pop"] = V.loc[fx, "pop_fix"].astype(float)
fx = V.town_fix.ne("")
V.loc[fx & V.town_fix.ne(V.loc_label), "loc"] = ""            # the located-in place was a county, not the town
V.loc[fx, "loc_label"] = V.loc[fx, "town_fix"]
fx = V.name_fix.ne("")
V.loc[fx, "name"] = V.loc[fx, "name_fix"]
V["fixed"] = V.cap_fix.ne("") | V.pop_fix.ne("")
assert (V[V.fixed].fix_source != "").all()
KIND_FIX = {"Q2698412": "other", "Q4357227": "other", "Q1427761": "tennis",     # an Olympic ceremonies theatre, the ancient stadium at Olympia
            "Q1154329": "winter", "Q576783": "winter", "Q322258": "winter",       # biathlon stadiums at Oberhof, Antholz and Ruhpolding
            "Q604681": "arena"}                                                  # Forum di Milano, an indoor arena
for q, k in KIND_FIX.items():
    V.loc[V.qid == q, "kind"] = k
# Sport guessed from names misses or mislabels some quoted cases; set by hand
SPORT_FIX = {"american": ["Q10862290", "Q373355", "Q1475645"], "baseball": ["Q5919963"], "soccer": ["Q857795", "Q4696834", "Q1817621", "Q8507", "Q854122", "Q1396145"],
             "hockey": ["Q96396965", "Q1607853"], "basketball": ["Q2927191"],
             "gaelic": ["Q4279491", "Q2571445", "Q3783904", "Q16632742", "Q3367645", "Q7071795", "Q3749236", "Q4019214", "Q3714840", "Q1822033", "Q3926094",
                        "Q7592697", "Q3776442", "Q3898486", "Q16632530", "Q1115980", "Q2421018", "Q3967624", "Q2924300", "Q1766163", "Q1821963"]}
for k, qs in SPORT_FIX.items():
    assert V.qid.isin(qs).sum() == len(qs), k
    V.loc[V.qid.isin(qs), "sport"] = k
# The nearest UK settlement within 4 km is kept as a cross-check only: used to fill missing populations it gave villages
# and hamlets for city grounds (Hillsborough, the Den), so no population is filled from it
fill_uk = pd.Series(False, index=V.index)
V.loc[fill_uk, "loc_label"] = V.loc[fill_uk, "uk_town"]; V.loc[fill_uk, "pop"] = V.loc[fill_uk, "uk_town_pop"]; V["pop_source"] = np.where(fill_uk, "uk settlement", "P131")
V["ratio"] = np.where(V["pop"] > 0, V.cap / V["pop"], np.nan)
use = V.verdict.isin(["ok", "unreviewed"]) & V.ratio.notna()
V["ratio_ok"] = np.where(use, V.ratio, np.nan)
GROUND = V.kind.isin(["ground", "arena"])
R = {}
rv = V[V.verdict != "unreviewed"]
R["n"] = dict(venues=len(V), with_pop=int(V["pop"].notna().sum()), countries=int(V.iso.replace("", np.nan).nunique()), multi_cap=int((V.n_caps > 1).sum()),
              multi_loc=int((V.n_locs > 1).sum()), uk=int((V.iso == "GB").sum()), uk_filled=int(fill_uk.sum()))
R["review"] = dict(n=len(rv), ok=int((rv.verdict == "ok").sum()), unchanged=int(((rv.verdict == "ok") & ~rv.fixed).sum()), fixed=int(((rv.verdict == "ok") & rv.fixed).sum()),
                   demolished=int(rv.reason.str.startswith("Demolished").sum()), district=int((rv.verdict == "district").sum()), wrong=int((rv.verdict == "wrong").sum()),
                   region=int((rv.verdict == "region").sum()), unsure=int((rv.verdict == "unsure").sum()))
R["review"]["corrected_pc"] = 100 * (len(rv) - R["review"]["unchanged"]) / len(rv)
raw1 = V[V.ratio_raw >= 1]
R["raw_fit"] = int(len(raw1))
assert (raw1.verdict != "unreviewed").all(), raw1[raw1.verdict == "unreviewed"][["name", "ratio"]]   # every case with a ratio of 1 or more was read
fit = V[(V.verdict == "ok") & (V.ratio >= 1)]
R["fit"] = dict(n=len(fit), grounds=int(fit.kind.isin(["ground", "arena"]).sum()), countries=int(fit.iso.nunique()), x2=int((fit.ratio >= 2).sum()))
R["fit_kind"] = fit.kind.value_counts().to_dict()
R["fit_sport"] = fit[fit.kind.isin(["ground", "arena"])].sport.replace("", "unknown").value_counts().to_dict()
R["fit_country"] = fit.groupby("country").size().sort_values(ascending=False).head(10).to_dict()


def row(r):
    return dict(qid=r.qid, name=r["name"], town=r.loc_label, pop=int(r["pop"]), cap=int(r.cap), ratio=round(float(r.ratio), 2), country=r.country, iso=r.iso,
                kind=r.kind, sport=r.sport, tenants=r.tenants[:80])


G = V[GROUND & V.ratio_ok.notna()].sort_values("ratio_ok", ascending=False)
okG = G[G.verdict == "ok"]
R["top_world"] = [row(r) for _, r in okG.head(15).iterrows()]
for k in ("motor", "horse", "winter", "bullring", "show", "tennis", "other"):
    s = V[(V.kind == k) & (V.verdict == "ok")].sort_values("ratio", ascending=False)
    R.setdefault("by_kind", {})[k] = [row(r) for _, r in s.head(5).iterrows()]
R["college"] = [row(r) for _, r in okG[(okG.iso == "US") & okG.tenants.str.contains(" football|Tigers|Spartans|Hokies|Terrapins|Crimson Tide|Mountaineers|Nittany", case=False) & ~okG.tenants.str.contains("national", case=False)].head(10).iterrows()]
R["nfl"] = [row(r) for _, r in okG[(okG.iso == "US") & okG.tenants.str.contains("Jets|Giants|Patriots|Bills|Lions", case=True)].head(6).iterrows()]
R["europe_soccer"] = [row(r) for _, r in okG[(okG.continent == "Europe") & (okG.sport == "soccer")].head(12).iterrows()]
R["uk"] = [row(r) for _, r in okG[okG.iso == "GB"].head(12).iterrows()]
R["ie"] = [row(r) for _, r in okG[okG.iso == "IE"].head(10).iterrows()]
R["uk_gaelic_ni"] = [row(r) for _, r in okG[(okG.iso == "GB") & (okG.sport == "gaelic")].head(5).iterrows()]
big = okG[(okG["pop"] < 25000)].sort_values("cap", ascending=False)
R["biggest_small_town"] = [row(r) for _, r in big.head(10).iterrows()]
# seats per head
cty = V[(V.verdict != "wrong") & (V.country_pop > 1e6)].groupby(["iso", "country"]).agg(n=("cap", "size"), seats=("cap", "sum"), cpop=("country_pop", "first")).reset_index()
cty = cty[cty.n >= 10]
cty["per1000"] = 1000 * cty.seats / cty.cpop
cty = cty.sort_values("per1000", ascending=False)
R["seats_top"] = [dict(iso=r.iso, country=r.country, n=int(r.n), seats=int(r.seats), per1000=round(float(r.per1000), 1)) for _, r in cty.head(12).iterrows()]
for iso in ("GB", "IE", "US", "DE", "ES", "IT", "FR", "AU", "BR", "CN", "IN", "JP", "NZ"):
    s = cty[cty.iso == iso]
    if len(s):
        R.setdefault("seats", {})[iso] = dict(country=s.country.iloc[0], n=int(s.n.iloc[0]), seats=int(s.seats.iloc[0]), per1000=round(float(s.per1000.iloc[0]), 1),
                                             rank=int(list(cty.iso).index(iso) + 1))
R["seats_n_countries"] = int(len(cty))
uk = V[(V.iso == "GB") & V.uk_town.ne("") & (V.pop_source == "P131")]
R["uk_agree_pc"] = 100 * float((uk.uk_town.map(norm) == uk.loc_label.map(norm)).mean())
named = {"Q692816": "beaver", "Q10862290": "metlife", "Q373355": "gillette", "Q543579": "clemson", "Q172732": "ims", "Q15910573": "pancho", "Q3776482": "machale",
         "Q242772": "horwich", "Q1817621": "guingamp", "Q1771247": "buriram", "Q8507": "lyon", "Q3135878": "chantilly", "Q7073774": "oakbank", "Q597004": "vaduz",
         "Q995161": "bryant_denny", "Q1766120": "nowlan", "Q854122": "lens", "Q1050220": "albayt", "Q847043": "notre_dame", "Q6729285": "bala", "Q618923": "newlawn",
         "Q45671": "anfield", "Q159848": "campnou", "Q128468": "wembley", "Q3967624": "clones", "Q2421018": "semple", "Q1822033": "aughrim",
         "Q3714840": "roscommon", "Q1115980": "killarney", "Q280878": "xanthi", "Q75300027": "stadler", "Q5919963": "lamade", "Q375365": "giants_stadium",
         "Q683112": "turfmoor", "Q857795": "aixovall"}
for q, k in named.items():
    r = V[V.qid == q].iloc[0]
    R.setdefault("v", {})[k] = dict(row(r), verdict=r.verdict, fixed=bool(r.fixed), cap_raw=int(r.cap_raw), pop_raw=None if pd.isna(r.pop_raw) else int(r.pop_raw), reason=r.reason)
R["median_ratio"] = float(V.ratio_ok.median())
cols = ["qid", "name", "country", "iso", "lon", "lat", "cap", "cap_raw", "cap_min", "n_caps", "loc", "loc_label", "pop", "pop_raw", "ratio", "kind", "sport", "tenants", "uk_town", "uk_town_pop", "uk_town_km", "verdict", "reason", "fix_source", "all_locs", "sitelinks"]
V[cols].round(5).to_csv(f"{DATA}/venues.csv", index=False)
K = ["ground", "arena", "motor", "horse", "winter", "bullring", "show", "tennis", "water", "other"]
S = ["soccer", "american", "baseball", "cricket", "rugby", "aussie", "gaelic", "hockey", "basketball", ""]
VC = {"ok": 0, "unreviewed": 0, "district": 1, "region": 1, "wrong": 2, "unsure": 3}
f = []
for _, r in V.iterrows():
    f.append([r.qid, r["name"], round(r.lon, 5), round(r.lat, 5), int(r.cap), None if pd.isna(r["pop"]) else int(r["pop"]), r.loc_label, None if pd.isna(r.ratio) else round(float(r.ratio), 3),
              K.index(r.kind), S.index(r.sport), r.country, VC[r.verdict], r.tenants[:90], r["loc"], int(r.verdict == "ok"), r.fix_source, r.reason if r.reason.startswith("Demolished") or "disused" in r.reason or "abandoned" in r.reason or "hillside" in r.reason else ""])
jsave({"fields": ["id", "name", "lon", "lat", "cap", "pop", "town", "ratio", "kind", "sport", "country", "v", "ten", "loc", "checked", "fix", "note"], "kinds": K, "sports": S, "f": f}, f"{DATA}/map.json")
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("n", "review", "raw_fit", "fit", "fit_kind", "fit_sport", "uk_agree_pc")}, ensure_ascii=False, indent=0))
for k in ("top_world", "uk", "ie", "college", "europe_soccer", "biggest_small_town", "seats_top"):
    print(k, [(x.get("name") or x.get("country"), x.get("town"), x.get("ratio") or x.get("per1000")) for x in R[k]])
print({k: [(x["name"], x["ratio"]) for x in v] for k, v in R["by_kind"].items()})
print(R["seats"])
