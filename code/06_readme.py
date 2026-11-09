"""Step 6: README.md, LICENSE and the Reddit post text (reddit/post.md), filled from data/results.json.
https://doi.org/10.5281/zenodo.24087795 and https://blog.tristanhotham.com/2026/10/31/stadium-towns/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
v, rv = R["v"], R["review"]
T = R["top_world"]
readme = f"""# Could your town fit in its stadium?

Sports venues bigger than the towns they stand in. The capacity of {R['n']['venues']:,} venues of 1,000 seats or more in Wikidata divided by the population of the place each stands in, with every case at the head of the ranking read by eye.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24087795}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/stadium-towns/}}
Code and data: {REPO}

## Headline results

- A first pass finds {R['raw_fit']} venues with more seats than their place has people; after reading each by eye, {R['fit']['n']} in {R['fit']['countries']} countries really are bigger than their town ({R['fit']['x2']} at least twice). {rv['corrected_pc']:.0f}% of the {rv['n']} venues checked were districts or suburbs of bigger cities ({rv['district']}), wrong figures or demolished venues ({rv['wrong']}), counties or boroughs ({rv['region']}), unsure ({rv['unsure']}), or real towns whose capacity or population needed correcting ({rv['fixed']}).
- Highest: GCS Ballpark, Sauget, Illinois ({T[0]['cap']:,} seats, {T[0]['pop']:,} people, {T[0]['ratio']:.1f}x); St Tiernach's Park, Clones, Ireland ({v['clones']['ratio']:.1f}x); Estadi Comunal d'Aixovall, Andorra ({v['aixovall']['ratio']:.1f}x); Xanthi FC Arena, Pigadia, unused since 2022 ({v['xanthi']['ratio']:.1f}x); Beaver Stadium, College Township ({v['beaver']['ratio']:.1f}x); MetLife Stadium, East Rutherford ({v['metlife']['ratio']:.1f}x).
- Kept apart: Oakbank Racecourse ({v['oakbank']['ratio']:.1f}x), the Indianapolis Motor Speedway ({v['ims']['ratio']:.1f}x), the Lago di Tesero ski stadium ({R['by_kind']['winter'][0]['ratio']:.1f}x).
- Britain and Ireland: GAA county grounds lead: St Tiernach's Park, Clones ({v['clones']['ratio']:.1f}x), Semple Stadium, Thurles ({v['semple']['ratio']:.1f}x), Aughrim County Ground ({v['aughrim']['ratio']:.1f}x); in Britain Victoria Stadium, Wincham ({R['uk'][0]['ratio']:.1f}x), Crabble, Maes Tegid and Bolton Wanderers' ground at Horwich ({v['horwich']['ratio']:.1f}x). Turf Moor seats {v['turfmoor']['ratio'] * 100:.0f}% of Burnley.
- Seats per 1,000 people in Wikidata's venues: Qatar {R['seats_top'][0]['per1000']:.0f}, Ireland {R['seats']['IE']['per1000']:.0f}, UK {R['seats']['GB']['per1000']:.0f}, US {R['seats']['US']['per1000']:.0f}.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | The interactive page: MapLibre on the OpenFreeMap Positron base map, every venue sized by seats and coloured by seats per resident, filters by kind, search, popups with sources, full-screen button. |
| `header.png` | Social card, 1200 x 630. |
| `data/venues.csv` | Every venue: capacity (as used, Wikidata's largest and smallest recorded), located-in place and population (as used and Wikidata's), ratio, kind and sport (guessed), tenants, nearest UK settlement (check only), verdict, reason and source of any hand correction. CC0 (from Wikidata). |
| `data/map.json` | Page data. CC0. |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `code/` | Numbered scripts, `overrides.csv` (every decision made by eye), templates, `qa.js`. |
| `img/`, `release/`, `reddit/` | Page figures; paper, blog post and Zenodo files; collage and post. |

## Method in brief

- Wikidata sports venues (Q1076486 and subclasses) with a capacity of at least 1,000; largest recorded capacity and largest recorded population; the located-in place with the smallest population.
- Checked by hand: current capacities for the quoted cases, and 2022 census populations (Central Statistics Office) for Irish towns, many of which have no population in Wikidata; each change and its source is in `code/overrides.csv`.
- Kind of venue and sport guessed from names and tenants; racecourses, circuits, winter sports venues, bullrings and showgrounds reported apart.
- Every venue with a ratio of 1 or more, and British and Irish venues down to 0.4, read by eye; a town counts if it is a municipality, township, commune or village in its own right.
- Caveats: outside the checked cases, old record capacities and census peaks, and some demolished venues; administrative populations differ between countries; coverage of Wikidata varies by country.

## How to rerun

Needs Python 3 with pandas, numpy, pyproj, shapely, matplotlib, Pillow; xelatex, pdftotext, pdfinfo; node with Playwright for `code/qa.js`. Raw inputs are listed in `code/common.py`; intermediates go to `ST_WORK`.

```
python3 code/01_stadiums.py     # venues, places, kinds, UK settlement check
python3 code/02_analysis.py     # overrides, ratios, results.json, data files
python3 code/03_figures.py      # figures
python3 code/04_build_site.py   # index.html
python3 code/05_paper.py        # paper PDF (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py       # collage and header.png
python3 code/06_readme.py       # README, LICENSE, Reddit post
python3 code/07_release.py      # blog post, Zenodo files
node code/qa.js                 # screenshots
```

## Sources and licences

- Venues, capacities, locations, populations, tenants and UK settlements: Wikidata (CC0), queried with QLever.
- Irish town populations: Central Statistics Office, Census of Population 2022. Current capacities of checked grounds: Wikipedia and club pages (sources per venue in `code/overrides.csv`).
- Countries and population estimates: Natural Earth (public domain). Base map: OpenFreeMap (OpenStreetMap data, ODbL); MapLibre GL JS (BSD 3-Clause).
- Code MIT; text and figures CC BY 4.0; derived data CC0.

## Citation

Hotham, T. (2026) Could your town fit in its stadium? Sports venues bigger than the towns they stand in. Zenodo. {{https://doi.org/10.5281/zenodo.24087795}}

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = open(os.path.join(ROOT, "..", "far-from-home", "LICENSE"), encoding="utf-8").read().split("Text and figures")[0] + """Text and figures: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Tristan Hotham, 2026.
Data (data/venues.csv, data/map.json, data/results.json): derived from Wikidata, CC0.
Fonts under the SIL Open Font License.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""**Title:** [OC] Could your town fit in its stadium? {R['fit']['n']} sports venues worldwide have more seats than their town has people

**Body:**

I divided the capacity of {R['n']['venues']:,} stadiums and arenas in Wikidata by the population of the town each stands in, then checked every case by eye.

- Record: GCS Ballpark in Sauget, Illinois: {T[0]['cap']:,} seats, {T[0]['pop']:,} residents ({T[0]['ratio']:.0f} seats each).
- Beaver Stadium (Penn State) could seat its township {v['beaver']['ratio']:.1f} times; MetLife Stadium seats East Rutherford, NJ {v['metlife']['ratio']:.1f} times.
- Ireland's GAA grounds: Clones (pop. {v['clones']['pop']:,}) fits in St Tiernach's Park {v['clones']['ratio']:.1f} times, Thurles in Semple Stadium {v['semple']['ratio']:.1f} times. Bolton's ground at Horwich ({v['horwich']['ratio']:.1f}x) is the only English Football League ground that holds its town; Turf Moor holds {v['turfmoor']['ratio'] * 100:.0f}% of Burnley.
- Kept apart: Oakbank Racecourse, Australia ({v['oakbank']['ratio']:.0f}x) and the Indianapolis Motor Speedway ({v['ims']['ratio']:.0f}x).
- {rv['corrected_pc']:.0f}% of the cases I checked were not right at first: Wikidata puts Camp Nou in one neighbourhood and Anfield in the district of Anfield, and still lists Giants Stadium, demolished in 2010.

Interactive map (tap any ground): {PAGE}

**Source comment:**

Data: Wikidata (CC0) via QLever; Natural Earth; Irish town populations from the 2022 census (CSO). Largest recorded capacity and population, with current capacities checked by hand for the quoted cases. Tools: Python (pandas, matplotlib), MapLibre. Code and every hand decision: {REPO}
"""
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
for txt in (readme, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in txt.replace("|---|---|", ""), bad
print("readme, licence, post written")
