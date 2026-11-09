/* Could your town fit in its stadium? Sports venues sized by capacity and coloured by seats per resident of their town,
 * on a plain OpenFreeMap base map. Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  const fmt = n => Number(n).toLocaleString('en-GB');
  const KL = { ground: 'stadium', arena: 'arena', motor: 'motor circuit', horse: 'racecourse', winter: 'winter sports venue', bullring: 'bullring', show: 'showground', tennis: 'tennis centre', water: 'water sports venue', other: 'venue' };
  const SL = { soccer: 'football', american: 'American football', baseball: 'baseball', cricket: 'cricket', rugby: 'rugby', aussie: 'Australian football', gaelic: 'Gaelic games', hockey: 'ice hockey', basketball: 'basketball', '': '' };
  const GROUPS = { all: null, ground: ['ground'], arena: ['arena'], race: ['motor', 'horse'], winter: ['winter'], other: ['bullring', 'show', 'tennis', 'water', 'other'] };
  let map = null, D = null, grp = qs.get('kind') || 'all', fitsOnly = qs.get('fits') === '1';
  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  function rec(i) { const r = D.f[i], o = {}; D.fields.forEach((k, j) => o[k] = r[j]); o.kindName = D.kinds[o.kind]; o.sportName = D.sports[o.sport]; return o; }
  function sentence(o) {
    if (o.v === 1) return `<div class="nt">The place Wikidata gives for it, ${esc(o.town)}, is a district or suburb of a larger city, so there is no town to compare.</div>`;
    if (o.v === 2) return `<div class="nt">Left out: ${o.note ? esc(o.note.charAt(0).toLowerCase() + o.note.slice(1)) + ' (checked by eye)' : 'the population or the venue in the data is wrong (checked by eye)'}.</div>`;
    if (o.v === 3) return `<div class="nt">Left out: the figures could not be confirmed.</div>`;
    if (o.ratio == null) return `<div class="nt">No population in Wikidata for the place it is in.</div>`;
    if (o.ratio >= 1) { const x = o.ratio >= 10 ? String(Math.round(o.ratio)) : o.ratio.toFixed(1);
      return `<div class="big">${x} times over</div><div>This town of ${fmt(o.pop)} people could sit in it ${x} times over.</div>`; }
    return `<div class="big">${Math.round(o.ratio * 100)}%</div><div>of the ${fmt(o.pop)} people of ${esc(o.town)} would fill it: one seat for every ${(1 / o.ratio).toFixed(1)} residents.</div>`;
  }
  function popup(i, ll) {
    const o = rec(i);
    const what = [KL[o.kindName], SL[o.sportName]].filter(Boolean).join(' · ');
    const h = `<b class="t">${esc(o.name)}</b><div class="nt">${esc(what)} · ${esc(o.town)}, ${esc(o.country)}</div>
      ${sentence(o)}
      <table><tr><td>seats</td><td>${fmt(o.cap)}</td></tr>${o.pop ? `<tr><td>${esc(o.town)}</td><td>${fmt(o.pop)} people</td></tr>` : ''}${o.ten ? `<tr><td>home to</td><td>${esc(o.ten)}</td></tr>` : ''}</table>
      <div class="lk"><a href="https://www.wikidata.org/wiki/${esc(o.id)}" target="_blank" rel="noopener">venue on Wikidata</a>${o.loc ? `<a href="https://www.wikidata.org/wiki/${esc(o.loc)}" target="_blank" rel="noopener">${esc(o.town)} on Wikidata</a>` : ''}</div>
      ${o.note && o.v !== 2 ? `<div class="nt">${esc(o.note.replace(/^A town or municipality in its own right; /, '').replace(/^./, c => c.toUpperCase()))}.</div>` : ''}
      <div class="nt">${o.fix ? 'Checked by hand. ' + esc(o.fix) + '.' : 'Largest capacity and largest population recorded in Wikidata.' + (o.checked ? ' Checked by eye.' : '')}</div>`;
    new maplibregl.Popup({ maxWidth: '310px' }).setLngLat(ll).setHTML(h).addTo(map);
  }
  function filt() {
    const g = GROUPS[grp];
    const f = ['all'];
    if (g) f.push(['in', ['get', 'k'], ['literal', g.map(k => D.kinds.indexOf(k))]]);
    if (fitsOnly) f.push(['>=', ['get', 'r'], 1], ['==', ['get', 'v'], 0]);
    ['vn', 'vnl'].forEach(l => map.getLayer(l) && map.setFilter(l, l === 'vnl' ? ['all', f, ['>=', ['get', 'r'], 1], ['==', ['get', 'v'], 0]] : f));
    document.querySelectorAll('.chip[data-g]').forEach(b => b.setAttribute('aria-pressed', b.dataset.g === grp));
  }
  function setup() {
    const before = (map.getStyle().layers.find(l => l.type === 'symbol') || {}).id;
    const ix = {}; D.fields.forEach((k, i) => ix[k] = i);
    const feats = D.f.map((r, i) => ({ type: 'Feature', properties: { i, c: r[ix.cap], r: r[ix.ratio] == null || r[ix.v] !== 0 ? -1 : r[ix.ratio], v: r[ix.v], k: r[ix.kind], n: r[ix.name] }, geometry: { type: 'Point', coordinates: [r[ix.lon], r[ix.lat]] } }));
    feats.sort((a, b) => b.properties.c - a.properties.c);          // small circles drawn on top of big ones
    map.addSource('vn', { type: 'geojson', data: { type: 'FeatureCollection', features: feats }, attribution: 'Venues: <a href="https://www.wikidata.org/" target="_blank">Wikidata</a> (CC0)' });
    const col = ['case', ['<', ['get', 'r'], 0], '#B5B3AC', ['interpolate', ['linear'], ['ln', ['get', 'r']], Math.log(0.05), '#9DB7CF', Math.log(0.2), '#E9C46A', Math.log(0.5), '#E9A03B', 0, '#D9702C', Math.log(3), '#B8322A', Math.log(15), '#7E1B2A']];
    map.addLayer({ id: 'vn', type: 'circle', source: 'vn', paint: { 'circle-color': col, 'circle-opacity': 0.9, 'circle-stroke-color': '#FFFFFF', 'circle-stroke-width': 1,
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 2, ['interpolate', ['linear'], ['sqrt', ['get', 'c']], 31, 3, 320, 9], 8, ['interpolate', ['linear'], ['sqrt', ['get', 'c']], 31, 5, 320, 18], 14, ['interpolate', ['linear'], ['sqrt', ['get', 'c']], 31, 8, 320, 28]] } });
    map.addLayer({ id: 'vnl', type: 'symbol', source: 'vn', minzoom: 5, filter: ['all', ['>=', ['get', 'r'], 1], ['==', ['get', 'v'], 0]],
      layout: { 'text-field': ['concat', ['to-string', ['/', ['round', ['*', ['get', 'r'], 10]], 10]], '×'], 'text-font': ['Noto Sans Bold'], 'text-size': 11, 'text-offset': [0, 1.3], 'text-anchor': 'top' },
      paint: { 'text-color': '#7E1B2A', 'text-halo-color': '#fff', 'text-halo-width': 1.6 } });
    map.on('click', e => { const q = map.queryRenderedFeatures([[e.point.x - 4, e.point.y - 4], [e.point.x + 4, e.point.y + 4]], { layers: ['vn'] }); if (q.length) popup(q[q.length - 1].properties.i, e.lngLat); });
    map.on('mouseenter', 'vn', () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', 'vn', () => map.getCanvas().style.cursor = '');
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    const vis = (id, v) => { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none'); };
    document.getElementById('lyVn').addEventListener('change', e => vis('vn', e.target.checked));
    document.getElementById('lyRl').addEventListener('change', e => vis('vnl', e.target.checked));
    document.getElementById('lyLbl').addEventListener('change', e => map.getStyle().layers.filter(l => l.type === 'symbol' && l.id !== 'vnl').forEach(l => vis(l.id, e.target.checked)));
    const fo = document.getElementById('lyFit'); fo.checked = fitsOnly; fo.addEventListener('change', e => { fitsOnly = e.target.checked; filt(); });
    document.querySelectorAll('.chip[data-g]').forEach(b => b.addEventListener('click', () => { grp = b.dataset.g; filt(); }));
    filt();
  }
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug'); let items = [], k = -1;
    const idx = D.f.map((r, i) => { const o = rec(i); return { i, n: o.name, s: o.town + ', ' + o.country + (o.ratio != null && o.v === 0 ? ' · ' + (o.ratio >= 1 ? o.ratio.toFixed(1) + ' seats a head' : Math.round(o.ratio * 100) + '% of the town') : ''), k: norm(o.name + ' ' + o.town + ' ' + o.ten), c: o.cap }; });
    const show_ = () => { const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1; if (v.length < 2) { sug.style.display = 'none'; return; }
      items = idx.filter(x => x.k.includes(v)).sort((a, b) => (b.k.startsWith(v) - a.k.startsWith(v)) || b.c - a.c).slice(0, 12);
      items.forEach((it, j) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.innerHTML = `${esc(it.n)} <span>${esc(it.s)}</span>`; li.addEventListener('mousedown', e => { e.preventDefault(); pick(j); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none'; };
    const pick = j => { const it = items[j]; if (!it) return; q.value = it.n; sug.style.display = 'none'; go(it.i); };
    q.addEventListener('input', show_);
    q.addEventListener('keydown', e => { const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show_(); pick(k < 0 ? 0 : k); } else if (e.key === 'Escape') sug.style.display = 'none'; });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }
  function go(i) {
    const o = rec(i); fold(true);
    if (grp !== 'all') { grp = 'all'; filt(); }
    if (fitsOnly && !(o.ratio >= 1 && o.v === 0)) { fitsOnly = false; document.getElementById('lyFit').checked = false; filt(); }
    map.flyTo({ center: [o.lon, o.lat], zoom: 12.5, duration: 1200 });
    map.once('moveend', () => popup(i, [o.lon, o.lat]));
  }
  window.__go = id => { const i = D.f.findIndex(r => r[0] === id); if (i >= 0) { document.getElementById('mapWrap').scrollIntoView({ behavior: 'smooth' }); setTimeout(() => go(i), 400); } };
  fetch('data/map.json').then(r => r.json()).then(d => {
    D = d;
    const at = (qs.get('at') || '').split(',').map(Number);
    const mo = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { center: small ? [-4, 53] : [-12, 51], zoom: small ? 3.6 : 4.1 };
    const m0 = new maplibregl.Map(Object.assign({ container: 'map', style: STYLE, attributionControl: { compact: true }, maxZoom: 17 }, mo));
    return new Promise((res, rej) => { m0.once('load', () => res(m0)); m0.once('error', e => { if (!m0.loaded()) rej(e.error || e); }); });
  }).then(mm => {
    map = mm; window.__map = mm;
    mm.on('error', e => { const er = e && e.error; if (er && (er.name === 'AbortError' || /abort/i.test(er.message || ''))) return; console.error(er || e); });
    const n = document.getElementById('nojs'); if (n) n.remove();
    mm.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    mm.once('idle', foldAt); setTimeout(foldAt, 1500);
    setup(); setupSearch();
    if (qs.get('open')) window.__go(qs.get('open'));
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.keys,.mfs-btn,.maplibregl-ctrl')) return; fold(true); }, { capture: true, passive: true, once: true });
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
