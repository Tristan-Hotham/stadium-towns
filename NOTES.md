# stadium-towns: working notes

Brief: /home/claude/work/new10/BRIEFS.md (study 5) + shared rules in /home/claude/work/new8/BRIEFS.md, /home/claude/work/new9/BRIEFS.md
and /home/claude/newdata/BRIEF.md. Format refs: studies/river-names, church-orientation, sunless-valleys; MapLibre page pattern
from studies/tower-shadows; code layout shared with studies/far-from-home (same batch). Work files: /home/claude/scratch/stadium-towns.

## Pipeline
01_stadiums.py (Wikidata rows -> one record per venue: largest capacity, located-in places with largest population, town =
smallest populated place, kind and sport guessed from names and tenants, nearest UK settlement within 4 km as a check)
-> 02_analysis.py (overrides.csv, ratios, results.json, data files) -> 03_figures.py -> 04_build_site.py -> 05_paper.py
-> reddit/collage.py -> 06_readme.py -> 07_release.py -> qa.js

## Data checks
- Every venue with capacity / population >= 1 (321) read by eye, plus GB/IE venues down to 0.4 (39 more): 360 verdicts in
  code/overrides.csv: 211 ok, 133 district/suburb of a bigger city, 11 wrong (Kotor pop 562, Maspalomas 94, Queanbeyan 6,237,
  La Felguera 594, Sea Forest Waterway pop 0, two never-built stadiums: Kirkby Project, New Trafford; an auditorium; Thupatemee
  linked to Pathum Thani), 3 county/borough, 2 unsure (Waldstadion Weismain 18,000; Stade des Trois Tilleuls 40,000).
  02_analysis.py asserts that no venue with ratio >= 1 is unreviewed.
- Rule for "town": a municipality, township, commune, borough or village in its own right counts even if suburban (East
  Rutherford, Foxborough, Longeville-lès-Metz, Town of Claremont, City of Subiaco); a suburb, ward, freguesia or district that is
  only part of a city does not (Australian suburbs, Anfield, Camp Nou's district, Campanhã, Pacaembu...). Judgement calls:
  Pigadia (Xanthi), Aixovall, Hagåtña, Pago Pago, Gżira, Nes (Faroe) kept as towns; Glenorchy, Lauderdale, Prospect, Burslem,
  Twerton, Horfield treated as districts.
- UK nearest-settlement fill was tried and dropped: it gave villages for city grounds (Hillsborough 30x, Fossetts Farm 162x).
  Kept as a check column only (agrees with P131 38% of the time).
- Kind regexes were checked against the matched names (Racecourse Ground = Wrexham football ground excluded; "Madejski",
  "Rice Stadium" no longer match winter). Sport guesses are rough (64 of 167 fitting grounds unknown).

## References and claims to verify (cited from memory)
- Bast and Buchhold (2017) QLever, CIKM 647 to 656; Vrandečić and Krötzsch (2014) Wikidata, CACM 57(10) 78 to 85; Natural Earth.
- Claims from memory: GCS Ballpark is a minor league ballpark (Gateway Grizzlies) in Sauget, an industrial village beside
  St Louis; MetLife is home of the Giants and Jets; Oakbank's racecourse holds its Easter meeting (Oakbank Easter Racing
  Carnival); Lago di Tesero hosts the Nordic World Ski Championships (Val di Fiemme); Qatar built stadiums for the 2022 World
  Cup; Pancho Arena is home of the Puskás Academy; Bolton Wanderers' stadium is in Horwich; FC Metz's Saint-Symphorien is in
  Longeville-lès-Metz; Victoria Stadium Wincham was Northwich Victoria's ground; Crabble is Dover's ground.
- Capacities and populations are Wikidata's largest recorded values (e.g. Sauget 141, Aixovall 69); spot-check the top five.

## Log
- All steps done: figures, page (QA desktop 1280 / phone 390), paper (9 pages, DOI fill tested), blog (6 figures), collage,
  header, README, LICENSE, Zenodo.

## Independent review (2026)
- Re-ran the pipeline: reproducible. Web-checked the top cases. Fixes, all in code/overrides.csv (new columns cap_fix, pop_fix,
  town_fix, name_fix, fix_source) and applied in 02_analysis.py after the first pass (raw_fit still uses Wikidata as it stands):
  - Irish GAA grounds: Wikidata has no population for Thurles, Clones, Cavan, Portlaoise, Carrick-on-Shannon, Aughrim, Birr...
    and puts Fitzgerald Stadium and Dr Hyde Park in their counties, so the biggest Irish cases were missing. Added CSO 2022
    census-town populations (citypopulation.de) and current capacities (Wikipedia list of GAA stadiums). St Tiernach's Park,
    Clones (29,000 / 1,885 = 15.4) is now 2nd in the world; Semple Stadium 5.6; Aughrim County Ground (Wikidata's "O'Byrne
    Park") 4.9. MacHale Park was 42,000 (old figure), now about 28,000 for 13,054 people = 2.1 (was quoted as 3.5).
  - Demolished venues marked wrong: Giants Stadium (2010), Foxboro Stadium, Valascia, Blyth Arena, Pontiac Silverdome, Palmer Stadium.
  - Current capacities: Xanthi FC Arena 7,244 (disused since 2022), Notre Dame 77,622, Bryant-Denny 100,077, Turf Moor 21,944,
    Athletic Grounds 18,500, Healy Park 17,636. Aixovall population 80 (2023). Stadler Stadion noted as abandoned.
  - Kinds: Oberhof, Antholz and Ruhpolding biathlon stadiums to winter; Forum di Milano to arena. Sport regex no longer calls
    "Giants/Lions/Tigers" baseball; sports set by hand for quoted cases and GAA grounds.
- Not verified: Aigeira Municipal Stadium 8,230; Fraher Field (15,000 vs 3,600 in sources); Gillette 68,756 may be pre-2023.
- References verified: Bast and Buchhold 2017 (CIKM 647 to 656, doi 10.1145/3132847.3132921); Vrandecic and Krotzsch 2014 CACM 57(10) 78 to 85.
