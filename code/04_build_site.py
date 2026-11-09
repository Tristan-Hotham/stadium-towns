"""Step 4: index.html from code/page_template.html, filled from data/results.json, with the facts stated in words checked.
10.5281/zenodo.24087795, https://doi.org/10.5281/zenodo.24087795 and https://blog.tristanhotham.com/2026/10/31/stadium-towns/ stay as placeholders for the publisher."""
import time
from PIL import Image
from common import *

R = jload(f"{DATA}/results.json")
T, v = R["top_world"], R["v"]
# facts stated in words
assert [t["qid"] for t in T[:6]] == ["Q5513049", "Q3967624", "Q857795", "Q280878", "Q692816", "Q10862290"]
assert R["college"][3]["name"] == "Stanford Stadium" and 0.95 < v["bryant_denny"]["ratio"] < 1.1
assert [x["qid"] for x in R["europe_soccer"][:4]] == ["Q857795", "Q280878", "Q75300027", "Q1483409"]
assert [x["town"] for x in R["ie"][:3]] == ["Clones", "Thurles", "Aughrim"]
assert {"Ballybofey-Stranorlar", "Roscommon", "Sixmilebridge", "Killarney", "Castlebar", "Cavan"} <= {x["town"] for x in R["ie"] if x["ratio"] >= 2}
assert R["ie"][0]["qid"] == v["clones"]["qid"] and v["semple"]["town"] == "Thurles" and v["aughrim"]["town"] == "Aughrim"
assert v["giants_stadium"]["verdict"] == "wrong" and "disused" in v["xanthi"]["reason"] and "abandoned" in v["stadler"]["reason"]
assert [x["town"] for x in R["uk"][:5]] == ["Wincham", "River", "Bala", "Ballinamallard", "Horwich"]
assert {"Enniskillen", "Armagh"} <= {x["town"] for x in R["uk"] if x["ratio"] >= 1}
assert 0.24 < v["turfmoor"]["ratio"] < 0.3 and v["anfield"]["verdict"] == "district" and v["campnou"]["verdict"] == "district"
assert R["seats_top"][0]["country"] == "Qatar" and R["seats"]["IE"]["rank"] == 2 and [x["country"] for x in R["seats_top"][2:5]] == ["Cyprus", "Uruguay", "New Zealand"]
assert R["by_kind"]["winter"][0]["qid"] == "Q26996740" and 16.5 < R["by_kind"]["winter"][0]["ratio"] < 17
assert max(t["cap"] for t in T) == v["beaver"]["cap"]
assert sum(1 for q in ("Q7744723", "Q133256842") if q) == 2


def rows(L):
    return "\n".join(f'<tr><td><a onclick="__go(\'{t["qid"]}\')">{t["name"]}</a></td><td>{t["town"]}, {t["country"].replace("United States of America", "US")}</td><td class="r">{t["cap"]:,}</td><td class="r">{t["pop"]:,}</td><td class="r">{t["ratio"]:.1f}</td></tr>' for t in L)


t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
fs = open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", fs).replace("{{TABLE_WORLD}}", rows(T[:12])).replace("{{TABLE_UKIE}}", rows(sorted(R["uk"][:8] + R["ie"][:8], key=lambda x: -x["ratio"])[:14]))
t = t.replace("{{REPO}}", REPO).replace("{{BYLINE}}", BYLINE).replace("{{AI}}", AI).replace("{{VERSION}}", time.strftime("%Y%m%d"))
t = fill(t, R)
t = re.sub(r'<img src="img/([\w.]+)" width="\d+" height="\d+"', lambda m: '<img src="img/%s" width="%d" height="%d"' % ((m.group(1),) + Image.open(f"{IMG}/{m.group(1)}").size), t)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= {"DOI", "DOI_URL", "BLOG_URL"}, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
js = open(os.path.join(ROOT, "js", "page.js"), encoding="utf-8").read()
assert "—" not in js and "–" not in js
print("index.html", len(t) // 1024, "KB")
