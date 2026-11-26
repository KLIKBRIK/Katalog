"""Rebuild _build/campaign_prices.json for one campaign from the team sheet 'KlikBrik Team Penjualan'
(Prima, 27 Nov 2026):
  python3 _build/campaign_tab.py "Black Friday" <bf_tab.json> <bundling_tab.json> <catalogue.json>
<bf_tab.json>       = values of 'Black Friday 2026'!A1:H200  (No. Set, Nama, Normal DM, Diskon, BF DM, BF Shopee, BF Toko, Berlaku di)
<bundling_tab.json> = values of 'Bundling BF 2026'!A1:K100  (Promo, Set utama, Bonus GRATIS, DM, Shopee, Toko, Cara pasang)
<catalogue.json>    = values of Catalogue!A5:M700 (only used to look up set numbers by name)
Rows whose "Berlaku di" says GRATIS SET are sold at the NORMAL price + a free bonus set (the BF discount is OFF);
"Paket Bonus" rows become bundles (main set + free bonus, one price per channel). Only public prices are written."""
import json, re, sys, os
B = os.path.dirname(os.path.abspath(__file__))
def vals(p):
    d = json.load(open(p)); return d['values'] if isinstance(d, dict) else d
def n(s):
    s = re.sub(r'\D', '', s or ''); return int(s) if s else None
name, bf_p, bu_p, cat_p = sys.argv[1:5]
bf = [r + [''] * 8 for r in vals(bf_p)[1:] if r and r[0].strip().isdigit()]
bu = [r + [''] * 7 for r in vals(bu_p)[1:] if r and r[0].strip()]
by_name = {}
for r in vals(cat_p):
    if r and r[0].strip().isdigit(): by_name.setdefault(r[1].strip().lower(), r[0].strip())
for r in bf: by_name[r[1].strip().lower()] = r[0].strip()
def no(t):
    k = by_name.get(t.strip().lower())
    if not k: sys.exit(f"ABORT: set '{t}' not found by name")
    return k
gifts = {no(r[1]): r for r in bu if r[0].strip().lower().startswith('gratis')}
items = {}
for r in bf:
    sn, berlaku = r[0].strip(), r[7].lower()
    it = dict(disc=r[3].strip().replace('.0%', '%'), dmN=n(r[2]), dmS=n(r[4]),
              mkt='none' if 'hanya dm' in berlaku else 'all', shpS=n(r[5]), tokS=n(r[6]))
    if 'gratis set' in berlaku:
        g = gifts.get(sn)
        if not g: sys.exit(f"ABORT: {sn} is GRATIS SET but has no row in the Bundling tab")
        it = dict(disc='', dmN=n(g[3]), dmS=n(g[3]), mkt='all', shpN=n(g[4]), tokN=n(g[5]),
                  gift=g[2].strip(), giftNo=no(g[2]))
    items[sn] = it
miss = set(gifts) - set(items)
if miss: sys.exit(f"ABORT: Gratis Set rows not in the BF tab: {miss}")
bundles = [dict(main=no(r[1]), mainName=r[1].strip(), gift=no(r[2]), giftName=r[2].strip(),
                dm=n(r[3]), shp=n(r[4]), tok=n(r[5]))
           for r in bu if r[0].strip().lower().startswith('paket')]
p = os.path.join(B, 'campaign_prices.json')
cp = json.load(open(p)) if os.path.exists(p) else {}
cp['_note'] = ("Public sale prices from the team sheet 'KlikBrik Team Penjualan' ('Black Friday 2026' + 'Bundling BF 2026' tabs, "
               "rebuilt with _build/campaign_tab.py). Items with 'gift' = normal price + free bonus set; '_bundles' = Paket Bonus. "
               "Shown on the site only while the campaign runs.")
cp[name] = items
cp.setdefault('_bundles', {})[name] = bundles
json.dump(cp, open(p, 'w'), indent=1, ensure_ascii=False, sort_keys=True)
print(f"OK {name}: {len(items)} sets ({sum(1 for i in items.values() if 'gift' in i)} Gratis Set, "
      f"{sum(1 for i in items.values() if i['mkt']=='none')} DM only), {len(bundles)} Paket Bonus")
