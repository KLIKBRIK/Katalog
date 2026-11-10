"""Rebuild the KlikBrik! catalogue site.
Usage (from repo root):
  python3 _build/build.py <catalogue_values.json> ["Updated date text"]
<catalogue_values.json> = Google Sheets values result for range Catalogue!A5:K700
of KlikBrik_Workbook (1tOwj3ar0kDT-qIenjcNpvpceLjm7aQiBOuVLZ01hXdE), as {"values":[[...],...]}.
Only public columns are used: set no, name, theme, where to sell, Shopee, Tokopedia,
IG/DM price, official store price (shown as "Harga Pasaran"), status, put in catalogue.
Photos: any img/<setno>.jpg (Prima's own template photos) is used instead of the online photo.
"""
import json, os, sys, shutil, datetime
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B)
src = json.load(open(sys.argv[1]))
if isinstance(src, list): src = json.loads(src[0]['text']) if 'text' in src[0] else {'values': src}
BULAN = "Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember".split()
d = datetime.date.today()
updated = sys.argv[2] if len(sys.argv) > 2 else f"{d.day} {BULAN[d.month-1]} {d.year}"
def n(s):
    s = (s or '').replace('Rp', '').replace(',', '').replace('.', '').strip()
    return int(s) if s.isdigit() else None
out = []
for r in src['values']:
    r = list(r) + [''] * 12
    if r[10] != 'Yes' or not r[0] or r[0] == 'Set No': continue
    theme = r[2].strip(); theme = 'Ideas' if theme.lower() == 'ideas' else theme
    o = dict(n=r[0].strip(), name=r[1].strip(), theme=theme, ch='dm' if r[3].startswith('DM') else 'all',
             shp=n(r[4]), tok=n(r[5]), dm=n(r[6]), ref=n(r[7]), st=r[9].strip())
    if o['dm']: out.append(o)
if len(out) < 100: sys.exit(f"ABORT: only {len(out)} sets parsed - check the sheet export, site NOT changed")
photos = sorted(f[:-4] for f in os.listdir(os.path.join(R, 'img')) if f.endswith('.jpg'))
t = open(os.path.join(B, 'template.html')).read()
html = (t.replace('__PHOTOS__', json.dumps(photos))
         .replace('__DATA__', json.dumps(out, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
         .replace('__REF_LABEL__', 'Harga Pasaran').replace('__UPDATED__', updated))
open(os.path.join(R, 'index.html'), 'w').write(html)
for f in ['logo-white.svg', 'wordmark-orange.png']: shutil.copy(os.path.join(B, f), R)
print(f"OK: {len(out)} sets, {len(photos)} own photos, updated {updated}")
