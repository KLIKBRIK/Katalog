"""Rebuild the KlikBrik! catalogue site.
Usage (from repo root):
  python3 _build/build.py <catalogue_values.json> [--guide <campaign_guide.json>] [--salelist <1111_sale_list.json>] [--date "text"] [--keep-prices]
--keep-prices (event-day runs, Prima 15 Nov 2026): prices, stock labels, set list, links and the "Harga per" date stay exactly as
published on the last weekly (Sunday) update; only today's campaign promo is added. Without it = full weekly update, which also
prints the price changes vs the published site (PRICE CHANGES / CHG lines) so the marketplaces can be updated once a week.
<campaign_guide.json> = values of 'Campaign Guide'!A6:J700, <1111_sale_list.json> = values of '11.11 Sale List'!A5:L600.
Only campaigns running today (Jakarta time) are put in the page.
<catalogue_values.json> = Google Sheets values result for range Catalogue!A5:M700
of KlikBrik_Workbook (1tOwj3ar0kDT-qIenjcNpvpceLjm7aQiBOuVLZ01hXdE), as {"values":[[...],...]}.
Only public columns are used: set no, name, theme, where to sell, Shopee, Tokopedia,
IG/DM price, official store price (shown as "Harga Pasaran"), status, put in catalogue, Stok KlikBrik (col M).
Photos: any img/<setno>.jpg (Prima's own template photos) is used instead of the online photo.
"""
import json, os, sys, shutil, datetime
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
import argparse
ap = argparse.ArgumentParser(); ap.add_argument('catalogue'); ap.add_argument('--guide'); ap.add_argument('--salelist'); ap.add_argument('--date'); ap.add_argument('--keep-prices', action='store_true')
A = ap.parse_args()
src = json.load(open(A.catalogue))
if isinstance(src, list): src = json.loads(src[0]['text']) if 'text' in src[0] else {'values': src}
BULAN = "Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember".split()
d = (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=7)).date()  # Jakarta
updated = A.date or f"{d.day} {BULAN[d.month-1]} {d.year}"
def n(s):
    s = (s or '').replace('Rp', '').replace(',', '').replace('.', '').strip()
    return int(s) if s.isdigit() else None
out = []; allrows = {}
for r in src['values']:
    r = list(r) + [''] * 14
    if r[0].strip().isdigit(): allrows[r[0].strip()] = r
    if r[10] != 'Yes' or not r[0] or r[0] == 'Set No': continue
    theme = r[2].strip(); theme = 'Ideas' if theme.lower() == 'ideas' else theme
    o = dict(n=r[0].strip(), name=r[1].strip(), theme=theme, ch='dm' if r[3].startswith('DM') else 'all',
             shp=n(r[4]), tok=n(r[5]), dm=n(r[6]), ref=n(r[7]), st=r[9].strip(), rs=1 if r[12].strip()=='Ready stock' else 0)
    if o['dm']: out.append(o)
best = {}
for o in out:
    if o['n'] not in best or o['dm'] < best[o['n']]['dm']: best[o['n']] = o
out = list(best.values())
if len(out) < 100: sys.exit(f"ABORT: only {len(out)} sets parsed - check the sheet export, site NOT changed")
import re
def published():
    try:
        h = open(os.path.join(R, 'index.html')).read()
        data = json.loads(re.search(r'const DATA = (\[.*?\]);\n', h, re.S).group(1))
        m = re.search(r'Harga per ([^.<]+)\.', h)
        return data, (m.group(1).strip() if m else None)
    except Exception:
        return None, None
pub, pub_date = published()
if A.keep_prices:
    if not pub or len(pub) < 100: sys.exit("ABORT: --keep-prices but the published page could not be read, site NOT changed")
    out = [dict(o) for o in pub if not o.get('x')]  # frozen weekly data (promo-only sets of old campaigns dropped)
    updated = A.date or pub_date or updated
camps = []
if A.guide:
    sys.path.insert(0, B); import campaigns
    camps = campaigns.active(A.guide, A.salelist)
    have = {o['n'] for o in out}
    for c in camps:
        for sn, it in c['items'].items():
            if sn in have or sn not in allrows: continue
            r = allrows[sn]; th = r[2].strip()
            out.append(dict(n=sn, name=r[1].strip(), theme='Ideas' if th.lower()=='ideas' else th,
                            ch='dm' if it['mkt']=='none' else 'all', shp=it.get('shpN'), tok=it.get('tokN'),
                            dm=it['dmN'], ref=n(r[7]), st=r[9].strip(), rs=1 if r[12].strip()=='Ready stock' else 0, x=1))
            have.add(sn)
# Sets Prima asked to keep on the site even when the sheet leaves them out (_build/catalogue_overrides.json).
_ov = os.path.join(B, 'catalogue_overrides.json')
if os.path.exists(_ov) and not A.keep_prices:
    have = {o['n'] for o in out}
    for sn, it in json.load(open(_ov)).get('include', {}).items():
        if sn in have or sn not in allrows: continue
        r = allrows[sn]; th = r[2].strip()
        out.append(dict(n=sn, name=r[1].strip(), theme='Ideas' if th.lower()=='ideas' else th, ch=it.get('ch', 'all'),
                        shp=it.get('shp'), tok=it.get('tok'), dm=it['dm'], ref=n(r[7]), st=it.get('st', r[9].strip()),
                        rs=1 if r[12].strip()=='Ready stock' else 0))
        have.add(sn)
# Direct links to each set's own Shopee / Tokopedia listing (_build/marketplace_links.json).
_ml = os.path.join(B, 'marketplace_links.json')
if os.path.exists(_ml) and not A.keep_prices:
    ml = json.load(open(_ml))
    for o in out:
        if o['n'] in ml.get('shopee', {}): o['su'] = ml['shopee'][o['n']]
        if o['n'] in ml.get('tokopedia', {}): o['tu'] = ml['tokopedia'][o['n']]
# Only show a marketplace where the set really has a listing (Prima, 15 Nov 2026).
for o in out:
    if not o.get('su'): o['shp'] = None
    if not o.get('tu'): o['tok'] = None
    if o['ch'] == 'all' and not (o.get('su') or o.get('tu')): o['ch'] = 'dm'
# Weekly report: what changed vs the published site (only on full updates).
if pub and not A.keep_prices:
    old = {o['n']: o for o in pub if not o.get('x')}; cnt = dict(dm=0, shp=0, tok=0); sets = 0
    for o in sorted(out, key=lambda o: o['n']):
        if o.get('x'): continue
        p = old.get(o['n'])
        if not p: print(f"CHG {o['n']} {o['name']}: NEW on site"); continue
        ch = [f"{f} {p.get(f)}->{o.get(f)}" for f in ('dm', 'shp', 'tok') if p.get(f) != o.get(f)]
        if p.get('rs') != o.get('rs'): ch.append('ready stock' if o.get('rs') else 'now pre-order')
        if ch:
            sets += 1; print(f"CHG {o['n']} {o['name']}: " + ', '.join(ch))
            for f in cnt: cnt[f] += p.get(f) != o.get(f)
    gone = sorted(set(old) - {o['n'] for o in out})
    for sn in gone: print(f"CHG {sn} {old[sn]['name']}: REMOVED from site")
    print(f"PRICE CHANGES vs last published: {sets} sets changed (DM {cnt['dm']}, Shopee {cnt['shp']}, Tokopedia {cnt['tok']}), {len(gone)} removed")
photos = sorted(f[:-4] for f in os.listdir(os.path.join(R, 'img')) if f.endswith('.jpg'))
t = open(os.path.join(B, 'template.html')).read()
html = (t.replace('__PHOTOS__', json.dumps(photos))
         .replace('__DATA__', json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
         .replace('__CAMP__', json.dumps(camps, separators=(',', ':')))
         .replace('__REF_LABEL__', 'Harga Pasaran').replace('__UPDATED__', updated))
open(os.path.join(R, 'index.html'), 'w').write(html)
for f in ['logo-white.svg', 'wordmark-orange.png']: shutil.copy(os.path.join(B, f), R)
# One landing page per set (set/<no>/), same data as the catalogue page.
sys.path.insert(0, B); import set_pages
n_pages, n_specs = set_pages.build(R, out, camps, set(photos), updated)
# New sets get a marketplace photo + Brickset specs via the "Marketplace assets" GitHub Action.
_st = os.path.join(R, '_marketplace', 'sets.txt')
if os.path.exists(_st):
    known = [l.strip() for l in open(_st) if l.strip()]
    new = sorted({o['n'] for o in out} - set(known))
    if new:
        open(_st, 'w').write('\n'.join(known + new) + '\n')
print(f"OK: {len(out)} sets, {n_pages} set pages ({n_specs} with specs), {len(photos)} own photos, campaigns today: {[(c['name'], len(c['items'])) for c in camps] or 'none'}, updated {updated}")
