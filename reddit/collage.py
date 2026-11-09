"""Reddit collage (r/dataisbeautiful style) and the 1200 x 630 header card.
Light background; no labels on land (the map carries colour only, names are in the list beside it); full legend; source footer.
Output: reddit/stadium_towns_collage.png (3000 x 2100 px) and header.png. Run after code/03_figures.py."""
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from figstyle import *

R = jload(f"{DATA}/results.json")
V = pd.read_csv(f"{DATA}/venues.csv", keep_default_na=False, na_values=[""])
OUT = os.path.join(ROOT, "reddit", "stadium_towns_collage.png")
FR = lambda size, w="bold": fm.FontProperties(fname=f"{FONTS}/FrauncesVar.ttf", size=size, weight=w)
CM = LinearSegmentedColormap.from_list("r", ["#9DB7CF", "#E9C46A", "#E9A03B", "#D9702C", "#B8322A", "#7E1B2A"])
NORM = LogNorm(0.05, 20)
SHORT = {"United States of America": "US", "United Kingdom": "UK"}


def worldbars(ax, L, fs=15):
    L = L[::-1]
    ys = np.arange(len(L))
    ax.barh(ys, [min(t["ratio"], 16) for t in L], color=[CM(NORM(t["ratio"])) for t in L], height=0.64)
    for y, t in zip(ys, L):
        ax.text(min(t["ratio"], 16) + 0.25, y, f"{t['ratio']:.1f}x" + (" >" if t["ratio"] > 16 else ""), va="center", family=MONO, fontsize=fs, color=INKC)
        ax.text(-0.25, y + 0.15, t["name"].replace("Memorial Stadium, Clemson", "Memorial Stadium"), ha="right", va="center", fontsize=fs, color=INKC)
        ax.text(-0.25, y - 0.24, f"{t['town']}, {SHORT.get(t['country'], t['country'])}: {t['cap']:,} seats, {t['pop']:,} people", ha="right", va="center", fontsize=fs - 4.5, color=MUT, family=MONO)
    ax.axvline(1, color=INKC, lw=1, ls=(0, (3, 2)))
    ax.set_xlim(0, 19); ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)


def ukmap(ax):
    f = plain_base(ax, 27700, (-10.6, 1.9, 49.9, 58.7))
    U = V[V.iso.isin(["GB", "IE"]) & V.verdict.isin(["ok", "unreviewed"]) & V.ratio.notna()].sort_values("ratio")
    x, y = f(U.lon.values, U.lat.values)
    ax.scatter(x, y, s=6 + U.cap.values / 700, c=[CM(NORM(r)) for r in U.ratio], edgecolor="white", lw=0.5, alpha=0.92, zorder=5)
    for s_ in ax.spines.values(): s_.set_visible(False)


def collage():
    fig = plt.figure(figsize=(15, 10.5), dpi=200); fig.patch.set_facecolor(PAPER)
    fig.text(0.035, 0.955, "Could your town fit in its stadium?", fontproperties=FR(42), color=INKC, va="top")
    fig.text(0.035, 0.885, f"Seats divided by the population of the town each ground stands in. {R['fit']['n']} venues worldwide are bigger than their town.", fontsize=17, color=MUT, va="top")
    fig.text(0.035, 0.83, "World: the whole town fits this many times", fontsize=17, color=INKC)
    ax = fig.add_axes([0.305, 0.25, 0.15, 0.56]); worldbars(ax, R["top_world"][:10], fs=13.5)
    # weekend venues
    k = [("Oakbank Racecourse", R["v"]["oakbank"]), ("Indianapolis Motor Speedway", R["v"]["ims"]), ("Lago di Tesero ski stadium", R["by_kind"]["winter"][0])]
    fig.text(0.035, 0.195, "One weekend a year (kept apart):", fontsize=16, color=INKC)
    for i, (nm, t) in enumerate(k):
        x0 = 0.035 + i * 0.155
        fig.text(x0, 0.165, f"{t['ratio']:.0f}x", fontproperties=FR(30), color="#7E1B2A", va="top")
        fig.text(x0, 0.105, f"{nm}\n{t['town']}, {t['pop']:,} people", fontsize=11.5, color=INKC, va="top", linespacing=1.3)
    # UK and Ireland
    fig.text(0.51, 0.83, "Britain and Ireland: seats per resident", fontsize=17, color=INKC)
    ax = fig.add_axes([0.48, 0.12, 0.29, 0.7]); ukmap(ax)
    L = sorted(R["ie"][:6] + R["uk"][:6], key=lambda t: -t["ratio"])[:12]
    ax2 = fig.add_axes([0.775, 0.1, 0.2, 0.71]); ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    for j, t in enumerate(L):
        yy = 0.98 - j * 0.07
        ax2.scatter([0.03], [yy - 0.012], s=110, color=CM(NORM(t["ratio"])), edgecolor="white")
        ax2.text(0.1, yy, t["name"], fontsize=12.5, color=INKC, va="top")
        ax2.text(0.1, yy - 0.026, f"{t['town']}: {t['ratio']:.1f}x", fontsize=11, color=MUT, family=MONO, va="top")
    yy = 0.98 - len(L) * 0.07 - 0.01
    ax2.text(0.0, yy, f"Horwich (Bolton Wanderers) is the only\nFootball League town that fits. Turf Moor\nholds {R['v']['turfmoor']['ratio'] * 100:.0f}% of Burnley.", fontsize=11, color=MUT, va="top")
    # legend
    lg = fig.add_axes([0.49, 0.07, 0.48, 0.035]); lg.axis("off"); lg.set_xlim(0, 1); lg.set_ylim(0, 1)
    for i, (r, lab) in enumerate(((0.1, "0.1"), (0.5, "0.5"), (1, "1: town fits"), (3, "3"), (15, "15+"))):
        lg.scatter([0.02 + i * 0.2], [0.5], s=120, color=CM(NORM(r))); lg.text(0.045 + i * 0.2, 0.5, lab, va="center", fontsize=12, color=INKC)
    fig.text(0.49, 0.045, "Seats per resident; circle size: seats. Grounds in city districts (Anfield, Wembley) are left out.", fontsize=11, color=MUT)
    fig.text(0.035, 0.012, f"Data: Wikidata (CC0), Natural Earth, CSO Census 2022. Every top case read by eye; {R['review']['corrected_pc']:.0f}% needed correcting.   maps.tristanhotham.com/stadium-towns",
             fontsize=11.5, family=MONO, color=MUT)
    fig.savefig(OUT, dpi=200, facecolor=PAPER)
    plt.close(fig)


def header():
    fig = plt.figure(figsize=(6, 3.15), dpi=200); fig.patch.set_facecolor(PAPER)
    fig.text(0.05, 0.86, "Could your town\nfit in its stadium?", fontproperties=FR(23), color=INKC, va="top", linespacing=1.0)
    b, m = R["v"]["beaver"], R["v"]["clones"]
    fig.text(0.05, 0.42, f"Beaver Stadium: {b['cap']:,} seats,\na township of {b['pop']:,}.\nClones fits in St Tiernach's Park {m['ratio']:.1f}x.", fontsize=10.5, color=INKC, va="top", linespacing=1.35)
    fig.text(0.05, 0.07, "Stadiums bigger than their towns", fontsize=8, color=MUT, family=MONO)
    ax = fig.add_axes([0.56, 0.06, 0.4, 0.88]); ukmap(ax)
    fig.savefig(os.path.join(ROOT, "header.png"), dpi=200, facecolor=PAPER)
    plt.close(fig)


collage(); header()
from PIL import Image
print(Image.open(OUT).size, Image.open(os.path.join(ROOT, "header.png")).size)
