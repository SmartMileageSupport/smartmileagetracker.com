# smartmileagetracker.com

Marketing site for **Smart Mileage Tracker** (App Store: [Smart Mileage: Tax Tracker](https://apps.apple.com/app/id6746294900)), the iOS app that detects drives automatically and logs mileage for IRS tax deductions.

Plain static HTML + one CSS file. No build step, no JavaScript, no frameworks, no cookies, no analytics. Hosted on GitHub Pages with the custom domain `smartmileagetracker.com` (DNS at Porkbun; MX records for `support@` are on Zoho — never touch them).

## Pages

| URL | File | Job |
|---|---|---|
| `/` | `index.html` | Landing page (App Store **Marketing URL**) |
| `/support` | `support.html` | Contact + FAQ (App Store **Support URL** — must show real contact info) |
| `/privacy` | `privacy.html` | Privacy policy (App Store **Privacy Policy URL**) |
| — | `404.html` | Not-found page, picked up automatically by Pages |

## Local preview

```
python3 -m http.server 8080
```

then open http://localhost:8080. Links are root-relative, so preview from the folder root (production is the domain root; the `*.github.io/<repo>/` path will look broken — that's expected and irrelevant).

## Regenerating images

The app screens are rendered from the app repo's screenshot pipeline (`../Smart Mileage Tracker/AppStore/build/`), not captured from a device. The two repos must sit side by side.

```
python3 tools/render-screens.py     # 8 raw screens -> img/screens/*.jpg (needs Chrome + Pillow)
```

Icon set — always from the REAL shipped icon (`AppIcon-1024-current.png`). The
`AppIcon-1024-refined.png` next to it is an unshipped lookalike redraw; the owner
does not want it representing the app (swapped out 2026-09-10):

```
SRC="../Smart Mileage Tracker/AppStore/icon/AppIcon-1024-current.png"
sips --resampleWidth 320 "$SRC" --out img/app-icon.png
sips --resampleWidth 180 "$SRC" --out img/apple-touch-icon.png
sips --resampleWidth 32  "$SRC" --out img/favicon-32.png
sips --resampleWidth 16  "$SRC" --out img/favicon-16.png
```

OG card (1200×630): edit `tools/og-image.html`, then render at 2× and downsample:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --screenshot=tools/.tmp/og-raw.png --window-size=1200,630 \
  --force-device-scale-factor=2 "file://$PWD/tools/og-image.html"
python3 -c "from PIL import Image; Image.open('tools/.tmp/og-raw.png').convert('RGB').resize((1200,630), Image.LANCZOS).save('img/og.png', optimize=True)"
```

`img/badge-app-store.svg` is Apple's official badge from the [App Store marketing tools](https://toolbox.marketingtools.apple.com/) — use unmodified, min 40px tall, with clear space; do not recolor or crop.

## Annual maintenance (January, and July if the IRS moves mid-year)

1. `grep -n "RATE-CHECK" *.html` — update every hit: the IRS cents-per-mile figure, the "$X a year you never claim" math (20 mi × 5 days × 52 weeks × rate), and the JSON-LD `aggregateRating` (refresh value/count from App Store Connect).
2. Bump `<lastmod>` in `sitemap.xml` for changed pages.
3. If policy or features changed, update `/privacy`'s "Last updated" date — and keep it consistent with the in-app policy text (`SettingsView.swift`, `PrivacyPolicyView`).
4. Copy guardrails: never claim "no in-app purchases" (a one-time unlock is planned; "no subscription" is the durable promise), and screens show sample data at each year's own rates — keep captions rate-agnostic.
5. Identity guardrails: the owner's personal name and email stay OFF this site and out of this repo's git history — copyright reads "© 2026 Smart Mileage Tracker", JSON-LD author is the Organization, and commits use the SmartMileageSupport noreply identity (set in this repo's local git config).

## Design notes

Light-only by choice (`color-scheme: light`; the app's marketing identity is the clean light look). Brand accent `#499EE9`, text-accent `#1C74C4` for contrast; the app's dark-mode accent `#52BBED` is reserved if a dark theme is ever added. Device frames are pure CSS — renders are square-cornered on purpose, the frame does the rounding, and the mockups carry their own status bar and Dynamic Island.
