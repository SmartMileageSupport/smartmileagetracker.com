#!/usr/bin/env python3
"""Renders the site's raw app screens from the app repo's screenshot pipeline.

    python3 tools/render-screens.py

Imports the mockup HTML/CSS from the app repo (AppStore/build) and renders each
screen alone — no marketing canvas, caption, or bezel — at 2x logical resolution,
then saves web-sized JPEGs into img/screens/. The site's CSS device frame adds
the bezel and corner rounding, so these renders are square-cornered on purpose.

Requires: Google Chrome (headless renderer) + Pillow, same as the app pipeline.
"""

import os
import subprocess
import sys

from PIL import Image

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_BUILD = os.path.join(os.path.dirname(SITE), "Smart Mileage Tracker",
                         "AppStore", "build")
sys.path.insert(0, APP_BUILD)

import build          # noqa: E402  (app_icon_uri — inlines the real app icon)
import screens        # noqa: E402
from style import CSS, SCREEN_W, SCREEN_H  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP = os.path.join(SITE, "tools", ".tmp")
OUT = os.path.join(SITE, "img", "screens")

# Undo the marketing-canvas geometry: page is exactly one screen, unscaled
# (Chrome's device-scale-factor supplies the 2x), square corners for the CSS frame.
OVERRIDES = f"""
html, body {{ width:{SCREEN_W}px; height:{SCREEN_H}px; }}
.screen {{ transform:none; }}
"""

SHOTS = [
    ("home", screens.screen_home),
    ("reports", screens.screen_reports),
    ("widget", lambda: screens.screen_widget(build.app_icon_uri())),
    ("lockscreen", screens.screen_lockscreen),
    ("notification", screens.screen_notification),
    ("swipe", screens.screen_swipe),
    ("yearend", screens.screen_yearend),
    ("privacy", screens.screen_privacy),
]

WEB_W = 640           # @2x for a ~320px CSS device frame
JPEG_QUALITY = 85


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    web_h = round(WEB_W * SCREEN_H / SCREEN_W)

    for name, fn in SHOTS:
        hp = os.path.join(TMP, name + ".html")
        with open(hp, "w") as f:
            f.write(f"<!doctype html><html><head><meta charset=\"utf-8\">"
                    f"<style>{CSS}</style><style>{OVERRIDES}</style></head>"
                    f"<body>{fn()}</body></html>")

        master = os.path.join(TMP, name + "@2x.png")
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--screenshot={master}", f"--window-size={SCREEN_W},{SCREEN_H}",
             "--force-device-scale-factor=2", "--virtual-time-budget=2500",
             f"file://{hp}"],
            check=True, capture_output=True,
        )

        im = Image.open(master).convert("RGB")
        assert im.size == (SCREEN_W * 2, SCREEN_H * 2), f"{name}: {im.size}"
        out = os.path.join(OUT, name + ".jpg")
        im.resize((WEB_W, web_h), Image.LANCZOS).save(
            out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        print(f"  ok  {name}.jpg  {WEB_W}x{web_h}  "
              f"{os.path.getsize(out) // 1024}KB")

    total = sum(os.path.getsize(os.path.join(OUT, f))
                for f in os.listdir(OUT) if f.endswith(".jpg"))
    print(f"\n{len(SHOTS)} screens -> {OUT}  ({total // 1024}KB total)")


if __name__ == "__main__":
    if not os.path.exists(CHROME):
        sys.exit("Google Chrome not found - it is used as the headless renderer.")
    main()
