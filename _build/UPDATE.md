# Updating the KlikBrik! catalogue site

## Weekly prices (Prima, 15 Nov 2026)
Prices, stock labels and the set list change on the site ONCE A WEEK: the Sunday (Jakarta) run is the full update.
On any other day the site is only rebuilt when a campaign runs that day (Campaign Guide), with `--keep-prices`:
everything stays as published on Sunday and only the promo is added. Other days: no rebuild.
Exception: Prima explicitly asks for an update now -> full update.
The Sunday build prints `CHG <set> ...` lines + a `PRICE CHANGES` total vs last week: that list is what the team
updates on Shopee / Tokopedia, once a week, so marketplace prices match the site.
Shopee: the ~58 UNLISTED (hidden) listings stay unlisted - Prima switches them on/off herself per order. Never relist or
delete them; the link refresh below only collects live listings, so they get no Shopee button.

1. Read Google Sheet `KlikBrik_Workbook` (id 1tOwj3ar0kDT-qIenjcNpvpceLjm7aQiBOuVLZ01hXdE), range `Catalogue!A5:M700`, and save the raw values result as JSON (e.g. /tmp/cat.json).
   Also read 'Campaign Guide'!A6:J700 (→ /tmp/guide.json).
2. From the repo root: `python3 _build/build.py /tmp/cat.json --guide /tmp/guide.json` (Sunday / full update)
   or add `--keep-prices` (campaign day that is not a Sunday). `--salelist` was only for 11.11 and is no longer needed.
   - Only campaigns running TODAY in Jakarta time are written into the page (future sale prices never leak early). The page itself hides a campaign once its date has passed.
   - It aborts (exit 1) without touching the site if fewer than 100 sets parse.
3. If `git status` shows changes: commit and push to `main`. GitHub Pages republishes in ~1–2 minutes.

Rules: only the Catalogue tab is used (rows with "Put in catalogue?" = Yes). Never add costs, floor prices, Admin columns or sourcing info - this repo is public.
New own photos: put a 720x720 JPG as img/<setno>.jpg.

Stock: Admin column AZ "STOK KLIKBRIK (website)" (Ready stock / Pre-order, blank = Pre-order) → Catalogue column M → website badge.

Keep-on-site list: `_build/catalogue_overrides.json` "include" lists sets that stay on the site (with fixed prices) even if the sheet says "Put in catalogue?" = No. Remove an entry to let the sheet decide again.

Marketplace buttons: `_build/marketplace_links.json` holds each set's own Shopee item id and Tokopedia product path, so "Beli via Shopee / Tokopedia" opens the exact listing. Sets without an entry fall back to the shop page + copied set number.
Refresh it (needs Prima's browser, signed in to Shopee Seller Centre) whenever listings are added, deleted or delisted:
- Shopee: in seller.shopee.co.id, GET /api/v3/opt/mpsku/list/v2/get_product_list?SPC_CDS=<from the page's own requests>&SPC_CDS_VER=2&page_number=N&page_size=48&list_type=live_all → set no = parent_sku (or the 5-digit number in the name) → item id. Shop id 503293604.
- Tokopedia: from www.tokopedia.com, POST https://gql.tokopedia.com/graphql/ShopProducts (GetShopProduct, shopID 7495020848524330673, perPage 80, fmenu "etalase") → product_url path after /klikbrik/ (drop the ?extParam).

Set pages: build.py also writes one landing page per set at set/<no>/ (photo, price, buy buttons, specifications) via _build/set_pages.py, from the same data as the catalogue page. Specs (pieces, minifigs, age, year, box size, weight) come from _marketplace/specs.csv, filled by the "Marketplace assets" GitHub Action from Brickset. build.py appends any new site set to _marketplace/sets.txt; commit that too so the Action fetches its photo + specs (the pages show the specs from the next build on).

Visitor stats: GoatCounter (https://klikbrik.goatcounter.com, Prima's account, added 15 Nov 2026). The count.js line sits before </body> in template.html and set_pages.py.

Fixed prices: `_build/catalogue_overrides.json` "price" pins a set's website/DM price (and optionally "shp"/"tok") on every build,
whatever the sheet says, e.g. 11388 Venetian Neighbourhood Rp10,799,000 and 21330 Home Alone Rp8,729,000 (Prima, 21 Nov 2026).
Remove an entry to let the sheet decide again.

Campaign tab prices (Prima, 26 Nov 2026): `_build/campaign_prices.json` holds a campaign's own per-set sale prices
(DM, Shopee AND Tokopedia, e.g. from the 'Black Friday 2026' tab). While that campaign runs they replace the Campaign
Guide's prices; normal Shopee/Tokopedia prices stay the published site prices. Only public prices go in it (never cost/margin).

Gratis Set + Paket Bonus (Prima, 27 Nov 2026): the team sheet 'KlikBrik Team Penjualan' (id 1RoQGPgZ-MRu2rzMXGFk28MqXrr1RhbRHtbWQOYihPvw)
is the source for Black Friday: tab 'Black Friday 2026' (144 sets; "GRATIS SET" rows are sold at the NORMAL price + a free
bonus set, NOT discounted) and tab 'Bundling BF 2026' (Gratis Set bonus per set + 12 "Paket Bonus" bundles). Rebuild
campaign_prices.json from them with:
  python3 _build/campaign_tab.py "Black Friday" <bf_tab.json> <bundling_tab.json> <catalogue.json>
The promo tab then shows a "Paket Bonus" section above the grid, Gratis Set cards (green tag, normal price + bonus) and a
bundle box on the main set's page - all only while the campaign runs.
