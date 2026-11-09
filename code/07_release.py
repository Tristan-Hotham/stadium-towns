"""Step 7: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24087795, https://doi.org/10.5281/zenodo.24087795 and https://blog.tristanhotham.com/2026/10/31/stadium-towns/ stay as placeholders for the publisher."""
import shutil, zipfile, importlib.util
from PIL import Image
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "04_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks (and rebuilds index.html)
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Could_Your_Town_Fit_in_Its_Stadium"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
post = fill(open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read(), R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP, set(re.findall(r"\{\{([^|}]+)\}\}", post))
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS", "civil serv"):
    assert bad not in vis, bad
assert AI in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
v = R["v"]
meta = {"title": "Could your town fit in its stadium?",
        "slug": "stadium-towns",
        "excerpt": f"Beaver Stadium could seat its township {v['beaver']['ratio']:.1f} times over and Clones could fit in St Tiernach's Park {v['clones']['ratio']:.1f} times. I found every sports ground in the world bigger than its town, and checked each one by hand.",
        "seo_description": f"{R['fit']['n']} sports venues have more seats than their town has people: Beaver Stadium, MetLife, Irish GAA grounds such as Clones, and Bolton.",
        "tags": ["maps", "stadiums", "football", "GAA", "college football", "Wikidata", "data visualisation"],
        "header_alt": f"Title card reading 'Could your town fit in its stadium?' beside a map of Britain and Ireland with stadiums as coloured circles, the reddest in Ireland, and the line Beaver Stadium: {v['beaver']['cap']:,} seats, a township of {v['beaver']['pop']:,}."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for dd in ("code", "js"):
        for fn in sorted(os.listdir(os.path.join(ROOT, dd))):
            if fn.endswith(".pyc") or fn == "__pycache__" or fn.endswith(".png"):
                continue
            z.write(os.path.join(ROOT, dd, fn), f"{SLUG}/{dd}/{fn}")
    for fn in sorted(os.listdir(os.path.join(ROOT, "data"))):
        z.write(os.path.join(ROOT, "data", fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "\u201c").replace("''", "\u201d")
assert "\\" not in ab and "$" not in ab, ab
zmeta = {"title": "Could Your Town Fit in Its Stadium? Sports Venues Bigger than the Towns They Stand In",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive page: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/stadium-towns/}}.</p><p>Sources: Wikidata (CC0), queried with QLever; Natural Earth (public domain); Irish town populations from the CSO Census of Population 2022; current capacities of checked grounds from Wikipedia and club pages. Derived data CC0; text and figures CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["stadiums", "sports venues", "capacity", "small towns", "Gaelic games", "college football", "Wikidata", "data quality"],
         "license": "cc-by-4.0", "language": "eng",
         "notes": "Text and figures CC BY 4.0; code MIT; data derived from Wikidata, CC0.",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = json.dumps(zmeta, ensure_ascii=False) + json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
