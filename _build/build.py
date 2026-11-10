"""Rebuild the KlikBrik! catalogue site.
Usage (from repo root):
  python3 _build/build.py <catalogue_values.json> [--guide <campaign_guide.json>] [--salelist <1111_sale_list.json>] [--date "text"]
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
ap = argparse.ArgumentParser(); ap.add_argument('catalogue'); ap.add_argument('--guide'); ap.add_argument('--salelist'); ap.add_argument('--date')
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
photos = sorted(f[:-4] for f in os.listdir(os.path.join(R, 'img')) if f.endswith('.jpg'))
t = open(os.path.join(B, 'template.html')).read()
html = (t.replace('__PHOTOS__', json.dumps(photos))
         .replace('__DATA__', json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
         .replace('__CAMP__', json.dumps(camps, separators=(',', ':')))
         .replace('__REF_LABEL__', 'Harga Pasaran').replace('__UPDATED__', updated))
open(os.path.join(R, 'index.html'), 'w').write(html)
for f in ['logo-white.svg', 'wordmark-orange.png']: shutil.copy(os.path.join(B, f), R)
print(f"OK: {len(out)} sets, {len(photos)} own photos, campaigns today: {[(c['name'], len(c['items'])) for c in camps] or 'none'}, updated {updated}")
