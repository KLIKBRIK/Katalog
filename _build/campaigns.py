"""Parse Campaign Guide (+ optional 11.11 Sale List) into active campaigns for the site.
Only campaigns running TODAY (Asia/Jakarta) are returned, so future sale prices never
appear in the public page before the campaign starts."""
import json, re, datetime
MON = {m: i+1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
def n(s):
    s = (s or '').replace('Rp', '').replace(',', '').replace('.', '').strip()
    return int(s) if s.isdigit() else None
def load(path):
    src = json.load(open(path))
    if isinstance(src, list): src = json.loads(src[0]['text']) if 'text' in src[0] else {'values': src}
    return src['values']
def parse_dates(s):
    s = s.replace('–', '-').replace('—', '-').strip()
    m = re.match(r'(\d{1,2})(?:\s*([A-Za-z]{3})[a-z]*)?(?:\s*(\d{4}))?\s*-\s*(\d{1,2})\s*([A-Za-z]{3})[a-z]*\s*(\d{4})', s)
    if m:
        d1, m1, y1, d2, m2, y2 = m.groups()
        e = datetime.date(int(y2), MON[m2.lower()], int(d2))
        return datetime.date(int(y1 or y2), MON[(m1 or m2).lower()], int(d1)), e
    m = re.match(r'(\d{1,2})\s*([A-Za-z]{3})[a-z]*\s*(\d{4})', s)
    if m:
        d = datetime.date(int(m.group(3)), MON[m.group(2).lower()], int(m.group(1))); return d, d
    return None, None
def active(guide_path, salelist_path=None, today=None):
    today = today or (datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=7)).date()
    tok = {}
    if salelist_path:
        for r in load(salelist_path):
            r = list(r) + [''] * 14
            if r[0].strip().isdigit(): tok[r[0].strip()] = (n(r[10]), n(r[11]))  # Toko normal, Toko sale
    camps = {}
    for r in load(guide_path):
        r = list(r) + [''] * 12
        name, dates, setno = r[0].strip(), r[1].strip(), r[2].strip()
        if not name or not setno.isdigit(): continue
        s, e = parse_dates(dates)
        if not s or not (s <= today <= e): continue
        flag = r[5].lower()
        mkt = 'none' if 'do not' in flag else ('shopee' if 'shopee only' in flag else 'all')
        dmN, dmS = n(r[8]), n(r[9])
        if not dmN or not dmS or dmS >= dmN: continue
        it = dict(disc=r[4].strip(), dmN=dmN, dmS=dmS, mkt=mkt)
        if mkt != 'none':
            it['shpN'], it['shpS'] = n(r[6]), n(r[7])
            if mkt == 'all':
                tn, ts = tok.get(setno, (None, None)) if name == '11.11' else (None, None)
                it['tokN'], it['tokS'] = (tn, ts) if ts else (n(r[6]), n(r[7]))
        c = camps.setdefault(name, dict(name=name, start=s.isoformat(), end=e.isoformat(), items={}))
        c['items'][setno] = it
    return list(camps.values())
