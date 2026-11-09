"""Step 3: figures for the page (img/*.jpg), the blog (release/blog/b_*.png, 1800 px) and the paper (release/paper/f_*.png)."""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from PIL import Image
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from figstyle import *

R = jload(f"{DATA}/results.json")
V = pd.read_csv(f"{DATA}/venues.csv", keep_default_na=False, na_values=[""])
BLOG, PAPERD = f"{ROOT}/release/blog", f"{ROOT}/release/paper"
for d in (BLOG, PAPERD):
    os.makedirs(d, exist_ok=True)
CM = LinearSegmentedColormap.from_list("r", ["#9DB7CF", "#E9C46A", "#E9A03B", "#D9702C", "#B8322A", "#7E1B2A"])
NORM = LogNorm(0.05, 20)
KLAB = {"ground": "stadium", "arena": "arena", "motor": "motor circuit", "horse": "racecourse", "winter": "winter sports", "bullring": "bullring",
        "show": "showground", "tennis": "tennis", "other": "other"}


def out(fig, name, dpi=200):
    fig.savefig(f"{WORK}/{name}.png", dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    im = Image.open(f"{WORK}/{name}.png").convert("RGB")
    im.resize((1600, round(im.size[1] * 1600 / im.size[0])), Image.LANCZOS).save(f"{IMG}/{name}.jpg", quality=84, optimize=True)
    im.resize((1800, round(im.size[1] * 1800 / im.size[0])), Image.LANCZOS).save(f"{BLOG}/b_{name}.png", optimize=True)
    w = min(2000, im.size[0]); im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS).save(f"{PAPERD}/f_{name}.png", optimize=True)
    os.remove(f"{WORK}/{name}.png")


SHORT = {"United States of America": "US", "United Kingdom": "UK", "Faeroe Is.": "Faroe Islands"}


def bars(ax, L, maxx=None, fmt_x=lambda t: f"{t['ratio']:.1f}x"):
    L = L[::-1]
    ys = np.arange(len(L))
    ax.barh(ys, [t["ratio"] for t in L], color=[CM(NORM(t["ratio"])) for t in L], height=0.68)
    for y, t in zip(ys, L):
        ax.text(t["ratio"] * 1.02 + 0.05, y, fmt_x(t), va="center", family=MONO, fontsize=11, color=INKC)
        ax.text(-0.02 * (maxx or max(x["ratio"] for x in L)), y + 0.14, t["name"], ha="right", va="center", fontsize=12, color=INKC)
        ax.text(-0.02 * (maxx or max(x["ratio"] for x in L)), y - 0.26, f"{t['town']}, {SHORT.get(t['country'], t['country'])}: {t['cap']:,} seats, {t['pop']:,} people", ha="right", va="center", fontsize=9, color=MUT, family=MONO)
    ax.set_yticks([]); ax.set_xlim(0, (maxx or max(x["ratio"] for x in L)) * 1.15)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#E3E1DA", lw=0.8); ax.set_axisbelow(True)


# ---------------------------------------------------------------- 1. world top grounds
fig, ax = plt.subplots(figsize=(12, 8.6)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.42, right=0.95, top=0.82, bottom=0.11)
bars(ax, R["top_world"], maxx=45)
ax.axvline(1, color=INKC, lw=1, ls=(0, (3, 2)))
ax.set_xlabel("Seats per resident of the town the ground stands in (capacity / population)")
title(fig, "The whole town would fit", "Sports grounds with the most seats per resident of the town they stand in; every case of 1 or more read by eye")
foot(fig, "Data: Wikidata (CC0); current capacities and Irish 2022 census populations where checked by hand. maps.tristanhotham.com/stadium-towns")
out(fig, "world")

# ---------------------------------------------------------------- 2. scatter
G = V[V.kind.isin(["ground", "arena"]) & V.verdict.isin(["ok", "unreviewed"]) & V["pop"].gt(0)]
fig, ax = plt.subplots(figsize=(12, 9)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.1, right=0.96, top=0.85, bottom=0.13)
ax.scatter(G["pop"], G.cap, s=7, c=[CM(NORM(r)) for r in G.ratio], lw=0, alpha=0.75, rasterized=True)
xs = np.logspace(1, 7.5, 50)
for k, lab in ((1, "the whole town fits"), (0.1, "a tenth of the town"), (0.01, "one in a hundred")):
    ax.plot(xs, xs * k, color=INKC if k == 1 else MUT, lw=1.1 if k == 1 else 0.8, ls="-" if k == 1 else (0, (3, 2)))
    ax.text(1.25e3 / k * 1.35, 1.2e3, lab, ha="left", va="center", fontsize=11, color=INKC if k == 1 else MUT, path_effects=HALO)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(30, 4e7); ax.set_ylim(900, 3e5)
lab = {"beaver": (1.0, 1.0), "metlife": (1, 1), "ims": (1, 1), "pancho": (1, 1), "machale": (1, 1), "horwich": (1, 1), "turfmoor": (1, 1), "campnou": (1, 1), "wembley": (1, 1)}
OFF = {"beaver": (-10, 4, "right"), "metlife": (-10, -6, "right"), "ims": (-10, 0, "right"), "pancho": (-10, 0, "right"), "machale": (-10, -12, "right"), "clones": (-10, 0, "right"), "semple": (-10, 0, "right"),
       "horwich": (10, -2, "left"), "turfmoor": (10, -2, "left"), "bryant_denny": (10, 0, "left")}
for k, (dx, dy, ha) in OFF.items():
    t = R["v"][k]
    ax.scatter([t["pop"]], [t["cap"]], s=46, facecolor="none", edgecolor=INKC, lw=1.2, zorder=5)
    ax.annotate(f"{t['name']}, {t['town']}", (t["pop"], t["cap"]), xytext=(dx, dy), textcoords="offset points", fontsize=10.5, color=INKC, path_effects=HALO, va="center", ha=ha)
ax.set_xlabel("Population of the town or city the venue is in"); ax.set_ylabel("Seats")
for s in ("top", "right"): ax.spines[s].set_visible(False)
title(fig, "Seats against people", f"{len(G):,} stadiums and arenas in Wikidata with a capacity and a population for the place they are in")
foot(fig, "Data: Wikidata (CC0). maps.tristanhotham.com/stadium-towns")
out(fig, "scatter")

# ---------------------------------------------------------------- 3. other kinds
groups = [("Winter sports", R["by_kind"]["winter"][:4]), ("Racecourses and motor circuits", sorted(R["by_kind"]["horse"][:3] + R["by_kind"]["motor"][:1], key=lambda t: -t["ratio"])),
          ("Bullrings", R["by_kind"]["bullring"][:4]), ("Showgrounds and equestrian", [t for t in R["by_kind"]["show"] if t["ratio"] >= 1][:3])]
fig, axs = plt.subplots(4, 1, figsize=(12, 13), gridspec_kw={"height_ratios": [len(g[1]) for g in groups]}); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.45, right=0.93, top=0.87, bottom=0.06, hspace=0.55)
for ax, (labk, L) in zip(axs, groups):
    bars(ax, L, maxx=85)
    ax.set_title(labk, loc="left", fontsize=14.5, color=INKC, x=-0.75)
title(fig, "Racecourses, circuits, ski stadiums and bullrings", "They hold crowds far beyond their towns on a few days a year, so they are kept apart from the stadium ranking")
foot(fig, "Data: Wikidata (CC0). Seats per resident of the town. maps.tristanhotham.com/stadium-towns")
out(fig, "kinds")

# ---------------------------------------------------------------- 4. UK and Ireland map
fig = plt.figure(figsize=(12, 12.5)); fig.patch.set_facecolor(PAPER)
ax = fig.add_axes([0.0, 0.04, 0.6, 0.86])
f = plain_base(ax, 27700, (-10.6, 1.9, 49.9, 58.7))
U = V[V.iso.isin(["GB", "IE"]) & V.verdict.isin(["ok", "unreviewed"]) & V.ratio.notna()].sort_values("ratio")
x, y = f(U.lon.values, U.lat.values)
ax.scatter(x, y, s=4 + U.cap.values / 900, c=[CM(NORM(r)) for r in U.ratio], edgecolor="white", lw=0.5, alpha=0.9, zorder=5)
L = sorted(R["ie"][:7] + R["uk"][:7], key=lambda t: -t["ratio"])
placed = []
for i, t in enumerate(L, 1):
    r = V[V.qid == t["qid"]].iloc[0]
    xx, yy = f(r.lon, r.lat)
    # try right, left, above, below; take the first spot clear of the numbers already placed
    for dx, dy, ha, va in ((9000, 0, "left", "center"), (-9000, 0, "right", "center"), (0, 9000, "center", "bottom"), (0, -9000, "center", "top")):
        cx = xx + dx + (15000 if ha == "left" else -15000 if ha == "right" else 0); cy = yy + dy + (12000 if va == "bottom" else -12000 if va == "top" else 0)
        if all(abs(cx - px) > 32000 or abs(cy - py) > 26000 for px, py in placed): break
    ax.text(xx + dx, yy + dy, str(i), fontsize=11, family=MONO, color=INKC, fontweight="bold", va=va, ha=ha, zorder=9, path_effects=HALO)
    placed.append((cx, cy))
ax2 = fig.add_axes([0.61, 0.04, 0.37, 0.86]); ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
ax2.text(0, 0.99, "Where the town fits,\nBritain and Ireland", fontsize=15, color=INKC, va="top")
for j, t in enumerate(L):
    yy = 0.9 - j * 0.048
    ax2.text(0, yy, f"{j + 1:>2}", family=MONO, fontsize=11.5, color=RED, va="top")
    ax2.text(0.09, yy, t["name"], fontsize=12, color=INKC, va="top")
    ax2.text(0.09, yy - 0.022, f"{t['town']}: {t['ratio']:.1f} seats a head", family=MONO, fontsize=9.8, color=MUT, va="top")
yy = 0.9 - len(L) * 0.048 - 0.02
for k, labk in ((0.1, "0.1 seats a head"), (0.5, "0.5"), (1, "1: the town fits"), (3, "3 or more")):
    ax2.scatter([0.03], [yy], s=60, color=CM(NORM(k))); ax2.text(0.09, yy, labk, fontsize=10.5, color=MUT, va="center"); yy -= 0.027
ax2.text(0, yy - 0.01, "Circle size: capacity. Grounds in a district\nof a bigger city (Anfield, Wembley)\nare left out.", fontsize=10.5, color=MUT, va="top")
title(fig, "Small towns, big grounds", "Stadiums in Britain and Ireland by seats per resident of their town; GAA county grounds lead")
foot(fig, "Data: Wikidata (CC0), Natural Earth, CSO Census 2022 (Irish towns). maps.tristanhotham.com/stadium-towns")
out(fig, "ukie")

# ---------------------------------------------------------------- 5. seats per head
S = R["seats_top"][:12]
extra = [R["seats"][k] for k in ("US", "ES", "DE", "IT", "FR", "JP", "BR", "CN", "IN") if R["seats"][k]["rank"] > 12]
fig, ax = plt.subplots(figsize=(12, 8.4)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.25, right=0.95, top=0.83, bottom=0.13)
L = S + extra
ys = np.arange(len(L))[::-1]
for y, t in zip(ys, L):
    c = RED if t["country"] in ("Ireland", "United Kingdom") else BLUE
    ax.barh(y, t["per1000"], color=c, height=0.68, alpha=0.9)
    ax.text(t["per1000"] + 3, y, f"{t['per1000']:.0f}", va="center", family=MONO, fontsize=11, color=INKC)
    ax.text(-4, y, t["country"].replace("United States of America", "United States"), ha="right", va="center", fontsize=12, color=INKC)
ax.axhline(ys[len(S) - 1] - 0.5, color=MUT, lw=0.8, ls=(0, (3, 2)))
ax.set_yticks([]); ax.set_xlabel("Seats in Wikidata's stadiums and arenas per 1,000 people")
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
title(fig, "Seats per head", f"The twelve countries with the most seats per person, then some big ones (countries of over a million with ten venues or more)")
foot(fig, "Data: Wikidata (CC0) venues of 1,000 seats or more; Natural Earth population estimates. Coverage varies by country.")
out(fig, "seats")

# ---------------------------------------------------------------- 6. checks
rv = R["review"]
fig, ax = plt.subplots(figsize=(12, 3.8)); fig.patch.set_facecolor(PAPER)
fig.subplots_adjust(left=0.05, right=0.97, top=0.62, bottom=0.3)
x = 0
for nm, v, c in (("a town in its own right", rv["unchanged"], BLUE), ("a town, with capacity or population corrected", rv["fixed"], "#5FA8A0"),
                 ("a district or suburb of a bigger city", rv["district"], RED), ("a wrong figure, or demolished", rv["wrong"], GOLD),
                 ("a county or borough", rv["region"], "#8E6BB0"), ("unsure", rv["unsure"], "#A3A3AD")):
    ax.barh(0, v, left=x, color=c, height=0.6, label=f"{nm} ({v})")
    if v > 20: ax.text(x + v / 2, 0, str(v), ha="center", va="center", color="white", family=MONO, fontsize=12)
    x += v
ax.set_xlim(0, x); ax.set_yticks([]); ax.set_xticks([])
for s in ax.spines.values(): s.set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3, frameon=False, fontsize=10.5)
title(fig, "Where the errors hide", f"Every venue with more seats than its place has people ({R['raw_fit']}), plus the British and Irish list, read by eye: {rv['corrected_pc']:.0f}% were not what they seemed", size=22)
foot(fig, "Data: Wikidata (CC0). maps.tristanhotham.com/stadium-towns")
out(fig, "checks")
print("figures done")
