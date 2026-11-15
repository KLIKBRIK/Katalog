# Updating the KlikBrik! catalogue site

1. Read Google Sheet `KlikBrik_Workbook` (id 1tOwj3ar0kDT-qIenjcNpvpceLjm7aQiBOuVLZ01hXdE), range `Catalogue!A5:M700`, and save the raw values result as JSON (e.g. /tmp/cat.json).
   Also read 'Campaign Guide'!A6:J700 (→ /tmp/guide.json) and '11.11 Sale List'!A5:L600 (→ /tmp/sale.json).
2. From the repo root: `python3 _build/build.py /tmp/cat.json --guide /tmp/guide.json --salelist /tmp/sale.json`
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
