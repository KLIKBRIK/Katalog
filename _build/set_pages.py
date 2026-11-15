"""One landing page per set: set/<no>/index.html (photo, price, buy buttons, specifications).
Called by build.py with the same data that goes into the catalogue page, so prices always match.
Specs come from _marketplace/specs.csv (Brickset: pieces, minifigs, age, year, box size, weight).
Public repo: only public fields are used here."""
import csv, html, json, os, re, shutil, urllib.parse

WA = "628126032772"
SHOPEE = "https://id.shp.ee/LodwY7vr"
TOKO = "https://www.tokopedia.com/klikbrik"
SITE = "https://klikbrik.github.io/Katalog/"
E = lambda s: html.escape(str(s), quote=True)
rp = lambda v: "Rp" + f"{v:,}".replace(",", ".")
slug = lambda t: re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", t.lower().replace("&", "and")))
wa = lambda t: "https://wa.me/" + WA + "?text=" + urllib.parse.quote(t)

CSS = """:root{--orange:#ff6000;--orange-deep:#e05400;--ink:#1c1f24;--ink-2:#2a2e35;--paper:#faf7f2;--card:#fff;--line:#ebe5dc;--muted:#6b6f76;--green:#127a46;--pink:#e0115f;--r:16px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--paper);color:var(--ink);line-height:1.45;-webkit-font-smoothing:antialiased}
a{color:inherit}
h1,h2{font-family:'Bricolage Grotesque',system-ui,sans-serif;line-height:1.08;letter-spacing:-.02em}
.wrap{max-width:1080px;margin:0 auto;padding:0 18px}
header{background:var(--ink);color:#fff}
.bar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 0}
.bar img{height:38px;display:block}
.bar a.back{font-size:14px;font-weight:700;text-decoration:none;border:1.5px solid rgba(255,255,255,.35);padding:8px 14px;border-radius:999px;white-space:nowrap}
.crumb{font-size:13px;color:var(--muted);padding:14px 0 0}
.crumb a{text-decoration:none;font-weight:700}
.top{display:grid;grid-template-columns:1.05fr 1fr;gap:26px;padding:14px 0 10px;align-items:start}
@media(max-width:760px){.top{grid-template-columns:1fr;gap:16px}}
.pic{position:relative;aspect-ratio:1/1;border-radius:var(--r);overflow:hidden;background:radial-gradient(circle at 50% 45%,#f6f6f6 0%,#ececec 55%,#e3e3e3 100%);border:1px solid var(--line)}
.pic img.full{width:100%;height:100%;object-fit:cover;display:block}
.pic img.box{position:absolute;left:12%;top:12%;width:76%;height:62%;object-fit:contain;mix-blend-mode:multiply}
.pic img.wm{position:absolute;right:3.5%;bottom:3%;width:18%}
.pic .fb{position:absolute;inset:0;display:none;align-items:center;justify-content:center;flex-direction:column;color:#9a9ea5;font-family:'Bricolage Grotesque',system-ui,sans-serif}
.pic .fb b{font-size:44px;color:#5d6168}
.pic.nofoto .fb{display:flex}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.tag{font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;background:#fff;border:1px solid var(--line);text-decoration:none}
.tag.theme{background:var(--ink);color:#fff;border-color:var(--ink)}
.tag.ret{background:#2a2e35;color:#fff;border-color:#2a2e35}
.tag.pre{background:#fff3c4;color:#6b4e00;border-color:#f3e2a0}
.tag.promo{background:var(--pink);color:#fff;border-color:var(--pink)}
h1{font-size:clamp(28px,4.4vw,42px);font-weight:800}
.setno{font-size:14px;font-weight:700;color:var(--muted);margin-top:6px}
.stk{display:inline-block;font-size:13px;font-weight:700;padding:5px 10px;border-radius:8px;margin-top:12px}
.stk.rs{background:#e6f4ec;color:var(--green)}
.stk.po{background:#f1eee9;color:var(--muted)}
.pricebox{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;margin-top:16px}
.lbl{font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.lbl.promo{color:var(--pink)}
.old{font-size:15px;color:var(--muted);text-decoration:line-through}
.now{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:800;font-size:34px;color:var(--orange-deep);line-height:1.1}
.save{display:inline-block;font-size:13px;font-weight:700;color:var(--green);background:#e6f4ec;padding:3px 9px;border-radius:6px;margin-top:4px}
.ends{font-size:13px;color:var(--pink);font-weight:700;margin-top:6px}
.btns{display:flex;flex-direction:column;gap:8px;margin-top:14px}
.btn{display:flex;align-items:center;justify-content:space-between;gap:8px;text-decoration:none;font-weight:700;font-size:15px;padding:13px 16px;border-radius:12px}
.btn.wa{background:var(--orange);color:#fff;justify-content:center}
.btn.wa:hover{background:var(--orange-deep)}
.btn.mp{background:#fff;border:1.5px solid var(--ink)}
.btn.mp s{color:#9a9ea5;font-weight:500;margin-right:4px}
.note{font-size:13px;color:var(--muted);line-height:1.4}
section{padding:22px 0}
section h2{font-size:26px;margin-bottom:12px}
table.spec{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}
.spec th,.spec td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--line);font-size:15px;vertical-align:top}
.spec tr:last-child th,.spec tr:last-child td{border-bottom:0}
.spec th{width:42%;color:var(--muted);font-weight:500}
.spec td{font-weight:700}
.trust{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
.t{background:var(--ink);color:#fff;border-radius:var(--r);padding:16px}
.t b{display:block;margin-bottom:4px}
.t p{font-size:14px;color:#c4c8ce}
.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}
.rel a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;text-decoration:none}
.rel a b{display:block;font-size:14px;line-height:1.25}
.rel a span{font-size:12px;color:var(--muted)}
.rel a i{display:block;font-style:normal;font-weight:800;color:var(--orange-deep);margin-top:4px}
footer{padding:26px 0 40px;font-size:12px;color:var(--muted);border-top:1px solid var(--line);margin-top:10px}
footer p+p{margin-top:6px}"""


def load_specs(path):
    if not os.path.exists(path):
        return {}
    return {r['set']: r for r in csv.DictReader(open(path))}


def photo(d, photos, mp):
    n, alt = d['n'], E(d['name'])
    if n in photos:
        return f'<img class="full" src="../../img/{n}.jpg" alt="{alt}">'
    if n in mp:
        return f'<img class="full" src="../../mp/{n}.jpg" alt="{alt}">'
    return (f'<img class="box" src="https://cdn.rebrickable.com/media/sets/{n}-1.jpg" alt="{alt}" '
            f'onerror="this.parentNode.classList.add(\'nofoto\');this.remove()">'
            f'<img class="wm" src="../../wordmark-orange.png" alt=""><div class="fb"><b>{n}</b><span>{E(d["theme"])}</span></div>')


def og_image(d, photos, mp):
    if d['n'] in photos: return SITE + f"img/{d['n']}.jpg"
    if d['n'] in mp: return SITE + f"mp/{d['n']}.jpg"
    return f"https://cdn.rebrickable.com/media/sets/{d['n']}-1.jpg"


def price_html(d, cp, camp):
    show_ref = d.get('ref') and d['ref'] > d['dm']
    normal = (f'<div><span class="lbl">Harga Pasaran</span> <span class="old">{rp(d["ref"])}</span></div>' if show_ref else '') + \
             f'<div class="lbl">Harga Spesial KlikBrik</div><div class="now">{rp(d["dm"])}</div>' + \
             (f'<span class="save">Hemat {rp(d["ref"] - d["dm"])}</span>' if show_ref else '')
    if not cp:
        return f'<div class="pricebox">{normal}</div>'
    end = camp['end']
    promo = (f'<div><span class="lbl">Harga normal</span> <span class="old">{rp(cp["dmN"])}</span></div>'
             f'<div class="lbl promo">Harga Promo {E(camp["name"])}</div><div class="now">{rp(cp["dmS"])}</div>'
             f'<span class="save">Hemat {rp(cp["dmN"] - cp["dmS"])}</span><div class="ends">Promo sampai {fmt_date(end)} 23.59 WIB</div>')
    return (f'<div class="pricebox" data-promo-end="{end}"><div class="p-promo">{promo}</div>'
            f'<div class="p-normal" hidden>{normal}</div></div>')


BULAN = "Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember".split()
def fmt_date(iso):
    y, m, d = iso.split('-')
    return f"{int(d)} {BULAN[int(m) - 1]} {y}"


def buttons(d, cp, camp):
    if cp:
        msg = f"Halo KlikBrik! Saya mau order PROMO {camp['name']}:\n{d['n']} {d['name']}\nHarga promo: {rp(cp['dmS'])} (normal {rp(cp['dmN'])})\n{'Ready stock' if d.get('rs') else 'Pre-order'}\nApakah masih bisa?"
    else:
        msg = f"Halo KlikBrik! Saya mau order:\n{d['n']} {d['name']}\nHarga Spesial KlikBrik: {rp(d['dm'])}\n{'Ready stock' if d.get('rs') else 'Pre-order'}\nApakah masih bisa?"
    out = [f'<a class="btn wa" href="{E(wa(msg))}" target="_blank" rel="noopener">Order Direct via WhatsApp</a>']
    shpN, shpS, tokN, tokS = d.get('shp'), None, d.get('tok'), None
    if cp and cp.get('mkt') != 'none':
        shpN, shpS = cp.get('shpN') or shpN, cp.get('shpS')
        if cp.get('mkt') == 'all':
            tokN, tokS = cp.get('tokN') or tokN, cp.get('tokS')
    if not d.get('su'): shpN = shpS = None
    if not d.get('tu'): tokN = tokS = None
    if d.get('ch') == 'all' and (shpN or tokN):
        def mp(label, shop, normal, sale, direct):
            if not (normal or sale): return ''
            pr = f'<s>{rp(normal)}</s> {rp(sale)}' if sale else rp(normal)
            return f'<a class="btn mp" href="{E(direct or shop)}" target="_blank" rel="noopener"><span>Beli via {label}</span><span>{pr}</span></a>'
        out.append(mp('Shopee', SHOPEE, shpN, shpS, d.get('su') and f"https://shopee.co.id/product/503293604/{d['su']}"))
        out.append(mp('Tokopedia', TOKO, tokN, tokS, d.get('tu') and f"https://www.tokopedia.com/klikbrik/{d['tu']}"))
        if cp and cp.get('mkt') == 'none':
            out.append('<p class="note">Harga promo hanya untuk order Direct via WhatsApp.</p>')
    else:
        out.append('<p class="note">Set ini khusus order Direct via WhatsApp.</p>')
    return '<div class="btns">' + ''.join(out) + '</div>'


def spec_rows(d, sp):
    rows = [("Nomor set", d['n']), ("Nama set", d['name']), ("Tema", d['theme'])]
    if sp.get('pieces'): rows.append(("Jumlah keping", f"{int(sp['pieces']):,}".replace(",", ".") + " keping"))
    if sp.get('minifigs') and sp['minifigs'] != '0': rows.append(("Minifigur", sp['minifigs']))
    if sp.get('age'): rows.append(("Usia", sp['age'] + " tahun"))
    if sp.get('year'): rows.append(("Tahun rilis", sp['year']))
    if sp.get('pack_cm'):
        rows.append(("Ukuran kotak", sp['pack_cm'].replace('.', ',').replace('x', ' × ') + " cm"))
    if sp.get('weight_g'):
        rows.append(("Berat (perkiraan)", f"{int(float(sp['weight_g'])) / 1000:.2f}".replace('.', ',') + " kg"))
    st = d.get('st', '')
    rows.append(("Status set", {"Retiring soon": "Segera retired", "Retired": "Retired", "Pre-order": "Segera rilis"}.get(st, "Tersedia")))
    rows.append(("Ketersediaan", "Ready stock — sudah ada di tangan kami" if d.get('rs') else "Pre-order — siap dikirim sekitar 3–7 hari"))
    rows.append(("Kondisi", "100% original LEGO®, baru & segel"))
    return ''.join(f'<tr><th>{E(k)}</th><td>{E(v)}</td></tr>' for k, v in rows)


def page(d, all_sets, camp, photos, mp, specs, updated):
    n, name, theme = d['n'], d['name'], d['theme']
    cp = camp['items'].get(n) if camp else None
    st = d.get('st', '')
    tags = [f'<a class="tag theme" href="../../?tema={slug(theme)}">{E(theme)}</a>']
    if cp: tags.append(f'<span class="tag promo" data-promo>{E(camp["name"])} −{E(cp["disc"])}</span>')
    if st == 'Retiring soon': tags.append('<span class="tag ret">Segera retired</span>')
    elif st == 'Retired': tags.append('<span class="tag ret">Retired</span>')
    elif st == 'Pre-order': tags.append('<span class="tag pre">Segera rilis</span>')
    stock = '<span class="stk rs">✓ Ready stock</span>' if d.get('rs') else '<span class="stk po">Pre-order · siap kirim ±3–7 hari</span>'
    sp = specs.get(n, {})
    pcs = (", " + f"{int(sp['pieces']):,}".replace(",", ".") + " keping") if sp.get('pieces') else ""
    desc = f"LEGO {theme} {n} {name}{pcs}. Original & segel, harga spesial {rp(d['dm'])} di KlikBrik!. Order via WhatsApp, Shopee atau Tokopedia."
    title = f"LEGO {theme} {n} {name} | KlikBrik!"
    same = [o for o in all_sets if o['theme'] == theme and o['n'] != n and not o.get('x')]
    same.sort(key=lambda o: abs(o['dm'] - d['dm']))
    rel = ''.join(f'<a href="../{o["n"]}/"><b>{E(o["name"])}</b><span>No. set {o["n"]}</span><i>{rp(o["dm"])}</i></a>' for o in same[:8])
    rel_html = f'<section><h2>Set {E(theme)} lainnya</h2><div class="rel">{rel}</div></section>' if rel else ''
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f"LEGO {theme} {n} {name}", "sku": n, "mpn": n,
          "brand": {"@type": "Brand", "name": "LEGO"}, "image": og_image(d, photos, mp), "description": desc,
          "offers": {"@type": "Offer", "priceCurrency": "IDR", "price": d['dm'], "url": SITE + f"set/{n}/",
                     "availability": "https://schema.org/InStock" if d.get('rs') else "https://schema.org/PreOrder",
                     "itemCondition": "https://schema.org/NewCondition"}}
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}set/{n}/">
<meta property="og:type" content="product">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{E(og_image(d, photos, mp))}">
<meta property="og:url" content="{SITE}set/{n}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')}</script>
</head>
<body>
<header><div class="wrap bar"><a href="../../"><img src="../../logo-white.svg" alt="KlikBrik!"></a><a class="back" href="../../">← Semua set</a></div></header>
<main class="wrap">
  <div class="crumb"><a href="../../">Katalog</a> › <a href="../../?tema={slug(theme)}">{E(theme)}</a> › {n}</div>
  <div class="top">
    <div class="pic">{photo(d, photos, mp)}</div>
    <div>
      <div class="tags">{''.join(tags)}</div>
      <h1>{E(name)}</h1>
      <div class="setno">LEGO® {E(theme)} · No. set {n}</div>
      {stock}
      {price_html(d, cp, camp)}
      {buttons(d, cp, camp)}
    </div>
  </div>
  <section><h2>Spesifikasi</h2><table class="spec">{spec_rows(d, sp)}</table></section>
  <section><h2>Kenapa beli di KlikBrik!</h2><div class="trust">
    <div class="t"><b>100% original & segel</b><p>Semua set LEGO® baru, kotak masih tersegel.</p></div>
    <div class="t"><b>Harga Direct lebih hemat</b><p>Order langsung via WhatsApp tanpa biaya marketplace.</p></div>
    <div class="t"><b>Aman via marketplace</b><p>Mau lebih tenang? Beli di toko resmi kami di Shopee / Tokopedia.</p></div>
  </div></section>
  {rel_html}
</main>
<footer><div class="wrap"><p>Harga per {E(updated)}. Harga dapat berubah sewaktu-waktu; harga final dikonfirmasi lewat chat.</p><p>LEGO® adalah merek dagang dari LEGO Group. KlikBrik! adalah toko independen dan tidak berafiliasi dengan LEGO Group.</p></div></footer>
<script>
(function(){{var b=document.querySelector('[data-promo-end]');if(!b)return;var t=new Date(Date.now()+7*3600e3).toISOString().slice(0,10);
if(t>b.getAttribute('data-promo-end')){{b.querySelector('.p-promo').hidden=true;b.querySelector('.p-normal').hidden=false;var g=document.querySelector('[data-promo]');if(g)g.remove();}}}})();
</script>
<script data-goatcounter="https://klikbrik.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


def build(root, out, camps, photos, updated):
    """Write set/<n>/index.html for every set on the site; remove pages of sets that left the site."""
    specs = load_specs(os.path.join(root, '_marketplace', 'specs.csv'))
    mpdir = os.path.join(root, 'mp')
    mp = {f[:-4] for f in os.listdir(mpdir) if f.endswith('.jpg') and '_' not in f} if os.path.isdir(mpdir) else set()
    camp = camps[0] if camps else None
    base = os.path.join(root, 'set')
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    sets = [d for d in out if not d.get('x') or (camp and d['n'] in camp['items'])]
    for d in sets:
        os.makedirs(os.path.join(base, d['n']))
        with open(os.path.join(base, d['n'], 'index.html'), 'w') as f:
            f.write(page(d, sets, camp, photos, mp, specs, updated))
    return len(sets), sum(1 for d in sets if specs.get(d['n'], {}).get('pieces'))
