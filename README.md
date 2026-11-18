# TeamKathleen.com

One-page fundraising site for Kathleen Bracken's 2027 Boston Marathon run for Girls on the Run
Greater Boston. Static HTML, published with GitHub Pages at https://teamkathleen.com.

## Run it locally

```bash
python3 -m http.server 8765
```

Then open http://127.0.0.1:8765/. Opening `index.html` straight from disk won't load the live
total or the donor names.

## What updates itself

`scripts/sync_givengain.py` reads the total raised and the public donor names from GivenGain and
writes `data/campaign.json`. The page reads that file for the progress bars and the finish tape.
It runs every morning through `.github/workflows/sync-givengain.yml`, and on demand from the
Actions tab ("Run workflow") or locally:

```bash
python3 scripts/sync_givengain.py
```

Only names GivenGain already shows publicly are published, each once. Anonymous donors, amounts,
and messages are never copied.

## What gets updated by hand

In `index.html`, near the bottom:

- `SPONSORS`: claimed miles, for example `{ 9: "Doane Stuart Class of 2009" }`
- `FINISH_SPONSOR`: the Finish Line sponsor's name

## Other files

- `contact.html`: contact form. Replace `FORM_ENDPOINT` with a form service URL before launch.
- `scripts/og.html`: source for `assets/og.png`, the link preview image (rebuild command inside).
- `assets/photos/`: web copies with all photo metadata (including location) removed.
- `_private/`: original photos, reference images, and working notes. Git-ignored; never published.
