# Could your town fit in its stadium?

Sports venues bigger than the towns they stand in. The capacity of 11,658 venues of 1,000 seats or more in Wikidata divided by the population of the place each stands in, with every case at the head of the ranking read by eye.

Interactive page: https://maps.tristanhotham.com/stadium-towns/
Paper: https://doi.org/10.5281/zenodo.24087795
Blog post: https://blog.tristanhotham.com/2026/10/31/stadium-towns/
Code and data: https://github.com/Tristan-Hotham/stadium-towns

## Headline results

- A first pass finds 321 venues with more seats than their place has people; after reading each by eye, 190 in 48 countries really are bigger than their town (73 at least twice). 50% of the 375 venues checked were districts or suburbs of bigger cities (133), wrong figures or demolished venues (17), counties or boroughs (3), unsure (2), or real towns whose capacity or population needed correcting (33).
- Highest: GCS Ballpark, Sauget, Illinois (6,000 seats, 141 people, 42.5x); St Tiernach's Park, Clones, Ireland (15.4x); Estadi Comunal d'Aixovall, Andorra (12.5x); Xanthi FC Arena, Pigadia, unused since 2022 (11.5x); Beaver Stadium, College Township (9.9x); MetLife Stadium, East Rutherford (8.2x).
- Kept apart: Oakbank Racecourse (80.9x), the Indianapolis Motor Speedway (18.4x), the Lago di Tesero ski stadium (16.9x).
- Britain and Ireland: GAA county grounds lead: St Tiernach's Park, Clones (15.4x), Semple Stadium, Thurles (5.6x), Aughrim County Ground (4.9x); in Britain Victoria Stadium, Wincham (2.2x), Crabble, Maes Tegid and Bolton Wanderers' ground at Horwich (1.4x). Turf Moor seats 27% of Burnley.
- Seats per 1,000 people in Wikidata's venues: Qatar 311, Ireland 210, UK 106, US 89.

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

Hotham, T. (2026) Could your town fit in its stadium? Sports venues bigger than the towns they stand in. Zenodo. https://doi.org/10.5281/zenodo.24087795

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
