"""Step 6: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Could_Your_Town_Fit_in_Its_Stadium.pdf and .tex beside the f_*.png figures.
The DOI stays a placeholder: the publisher reruns  DOI=10.5281/zenodo.N python3 code/05_paper.py  then 08_release.py."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Could_Your_Town_Fit_in_Its_Stadium"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
assert R["v"]["campnou"]["town"].startswith("La Maternitat i Sant Ramon") and R["v"]["campnou"]["verdict"] == "district"
assert 45 < R["review"]["corrected_pc"] < 55      # "half"
assert R["v"]["machale"]["cap_raw"] == 42000 and R["v"]["notre_dame"]["cap"] == 77622


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


def vtab(L, cap, lab):
    rows = "".join(f"{i} & {tex(t['name'])} & {tex(t['town'])}, {tex(t['country'].replace('United States of America', 'US'))} & {t['cap']:,} & {t['pop']:,} & {t['ratio']:.2f}\\\\\n" for i, t in enumerate(L, 1))
    return ("\\begin{table}[tbp]\\centering\\small\\caption{" + cap + "}\\label{" + lab + "}\\begin{tabular}{rp{4.6cm}p{4.2cm}rrr}\\toprule & Venue & Town & Seats & People & Seats a head\\\\\\midrule\n"
            + rows + "\\bottomrule\\end{tabular}\\end{table}")


TW = vtab(R["top_world"], "The fifteen stadiums and arenas with the most seats per resident of their town (checked by eye).", "tab:world")
TC = vtab(R["college"], "American college stadiums bigger than their town.", "tab:college")
TU = vtab(sorted(R["uk"][:8] + R["ie"][:8], key=lambda x: -x["ratio"])[:14], "Britain and Ireland: grounds with the most seats per resident of their town.", "tab:ukie")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{AI}}", AI).replace("{{TABLE_WORLD}}", TW).replace("{{TABLE_UKIE}}", TU).replace("{{TABLE_COLLEGE}}", TC)
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24087795", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l or l.startswith("!")][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
