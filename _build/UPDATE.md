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
