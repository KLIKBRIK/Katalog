"""Build marketplace assets for Shopee / Tokopedia bulk uploads.

For every set number in _marketplace/sets.txt:
  * mp/<set>.jpg  - 1000x1000 product photo in the KlikBrik marketplace style
                    (Prima's own photo from img/ if there is one, otherwise the
                    official set image on the light-grey KlikBrik background).
  * _marketplace/specs.csv - pieces, packaging size (cm) and weight (g) from
                    Brickset, used for parcel weight / dimensions.

Runs in GitHub Actions (.github/workflows/marketplace-assets.yml). Existing
outputs are kept, so re-runs only fetch new sets.
"""
import csv, html, io, os, re, sys, time
import urllib.request
from PIL import Image, ImageChops, ImageDraw, ImageFilter

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'mp')
SPECS = os.path.join(R, '_marketplace', 'specs.csv')
SKIP_OWN = {'10294'}  # own photo shows a store price sticker - use official image
UA = {'User-Agent': 'Mozilla/5.0 (KlikBrik catalogue builder; contact via github.com/KLIKBRIK)'}
S = 1000

os.makedirs(OUT, exist_ok=True)
sets = [l.strip() for l in open(os.path.join(R, '_marketplace', 'sets.txt')) if l.strip()]


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def background():
    bg = Image.new('RGB', (S, S))
    px = bg.load()
    cx, cy = S * 0.5, S * 0.45
    maxd = (S * S * 0.5) ** 0.5 * 1.05
    for y in range(S):
        for x in range(S):
            t = min(1.0, ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd)
            if t < 0.55:
                v = 246 - (246 - 236) * (t / 0.55)
            else:
                v = 236 - (236 - 227) * ((t - 0.55) / 0.45)
            px[x, y] = (int(v),) * 3
    return bg


BG = background()
WM = Image.open(os.path.join(R, 'wordmark-orange.png')).convert('RGBA')
wm_w = int(S * 0.18)
WM = WM.resize((wm_w, round(WM.height * wm_w / WM.width)), Image.LANCZOS)


def dark_background(im):
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3), (w // 2, 2), (w // 2, h - 3)]
    vals = [sum(im.getpixel(p)) / 3 for p in pts]
    return sum(v < 45 for v in vals) >= 4


def compose_dark(prod):
    # official photo on a dark background: fill the square with that dark tone
    tone = tuple(sorted(prod.getpixel(p)[i] for p in [(2, 2), (prod.width - 3, prod.height - 3)])[0] for i in range(3))
    canvas = Image.new('RGB', (S, S), tone)
    prod = prod.copy()
    prod.thumbnail((int(S * 0.92), int(S * 0.86)), Image.LANCZOS)
    canvas.paste(prod, ((S - prod.width) // 2, (S - prod.height) // 2 - int(S * 0.02)))
    canvas.paste(WM, (S - wm_w - int(S * 0.035), S - WM.height - int(S * 0.03)), WM)
    return canvas


def compose(raw):
    prod = Image.open(io.BytesIO(raw)).convert('RGB')
    if dark_background(prod):
        return compose_dark(prod)
    bw, bh = int(S * 0.76), int(S * 0.62)
    prod.thumbnail((bw, bh), Image.LANCZOS)
    x = (S - prod.width) // 2
    y = int(S * 0.12) + (bh - prod.height) // 2
    canvas = BG.copy()
    # product, multiplied onto the grey background (white areas disappear)
    layer = Image.new('RGB', (S, S), 'white')
    layer.paste(prod, (x, y))
    # reflection below the product
    rh = int(prod.height * 0.28)
    if rh > 4 and y + prod.height + 2 + rh <= S:
        refl = prod.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, prod.width, rh))
        mask = Image.new('L', (prod.width, rh))
        md = ImageDraw.Draw(mask)
        for i in range(rh):
            md.line([(0, i), (prod.width, i)], fill=int(255 * 0.28 * (1 - i / rh)))
        white = Image.new('RGB', refl.size, 'white')
        refl = Image.composite(refl, white, mask)
        layer.paste(refl, (x, y + prod.height + 2))
    canvas = ImageChops.multiply(canvas, layer)
    canvas.paste(WM, (S - wm_w - int(S * 0.035), S - WM.height - int(S * 0.03)), WM)
    return canvas


def num(s):
    s = s.replace(',', '')
    m = re.search(r'[\d.]+', s)
    return float(m.group()) if m else None


def brickset(n):
    page = get(f'https://brickset.com/sets/{n}-1')
    if not page:
        return {}
    t = page.decode('utf-8', 'ignore')
    d = {}
    for k, v in re.findall(r'<dt>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>', t, re.S):
        d[html.unescape(re.sub('<[^>]+>', '', k)).strip()] = html.unescape(re.sub('<[^>]+>', ' ', v)).strip()
    out = {}
    if d.get('Pieces'):
        out['pieces'] = int(num(d['Pieces']) or 0) or ''
    m = re.search(r'([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)\s*cm', d.get('Packaging size', ''))
    if m:
        out['pack_cm'] = 'x'.join(m.groups())
    w = d.get('Weight', '')
    m = re.search(r'([\d.]+)\s*kg', w, re.I)
    if m:
        out['weight_g'] = round(float(m.group(1)) * 1000)
    return out


specs = {}
if os.path.exists(SPECS):
    for row in csv.DictReader(open(SPECS)):
        specs[row['set']] = row

own = {f[:-4] for f in os.listdir(os.path.join(R, 'img')) if f.endswith('.jpg')} - SKIP_OWN
done_img = done_spec = 0
for i, n in enumerate(sets):
    dest = os.path.join(OUT, f'{n}.jpg')
    if not os.path.exists(dest):
        if n in own:
            im = Image.open(os.path.join(R, 'img', f'{n}.jpg')).convert('RGB')
            im.resize((S, S), Image.LANCZOS).save(dest, quality=88)
            done_img += 1
        else:
            raw = get(f'https://cdn.rebrickable.com/media/sets/{n}-1.jpg')
            if raw:
                try:
                    compose(raw).save(dest, quality=86, optimize=True)
                    done_img += 1
                except Exception as e:
                    print('image error', n, e)
    if n not in specs or not specs[n].get('checked'):
        info = brickset(n)
        specs[n] = {'set': n, 'pieces': info.get('pieces', ''), 'pack_cm': info.get('pack_cm', ''),
                    'weight_g': info.get('weight_g', ''), 'checked': '1'}
        done_spec += 1
        time.sleep(1.2)
    if i % 25 == 0:
        print(i, n, flush=True)

with open(SPECS, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['set', 'pieces', 'pack_cm', 'weight_g', 'checked'])
    w.writeheader()
    for n in sorted(specs):
        w.writerow(specs[n])

missing = [n for n in sets if not os.path.exists(os.path.join(OUT, f'{n}.jpg'))]
open(os.path.join(R, '_marketplace', 'missing_images.txt'), 'w').write('\n'.join(missing) + ('\n' if missing else ''))
print(f'images new: {done_img}, specs new: {done_spec}, missing images: {len(missing)}')
