"""Rebuild docs/demo.gif from real runs of this project.

Starts the Django dev server from a throwaway copy (so db.sqlite3 and media/ are never
touched), creates a throwaway demo user there, then drives the real site in Chrome with
Playwright: browse, filter by genre, step through books, log in, favourite a book, open the
favourites page, hit a missing book. It finishes by running `python manage.py test` and
replaying the output. Only the captions and the typing animation are added.

Needs db.sqlite3 (run `migrate` and `loaddata sample_books` first).

    pip install Pillow playwright
    python docs/demo/make_demo_gif.py [--channel chrome|msedge]
"""

from __future__ import annotations

import argparse
import io
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from termgif import BROWSER_SIZE, Scene, Timeline, with_caption

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "demo.gif"
TITLE = "The_Classics_shelf"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"}
DEMO_USER = "demo_reader"

# Lay the site out wider than the GIF and shrink it, so a whole row of covers fits.
SCALE = 0.75
VIEWPORT = {"width": round(BROWSER_SIZE[0] / SCALE), "height": round(BROWSER_SIZE[1] / SCALE)}


def run_merged(cmd: list[str], cwd: Path) -> list[str]:
    """stdout and stderr interleaved, as they would appear in a terminal."""
    proc = subprocess.run(
        cmd, cwd=cwd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8"
    )
    return proc.stdout.splitlines()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def record_site(site: Path, password: str, channel: str, tl: Timeline) -> None:
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}", "--noreload"],
        cwd=site, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(base + "/", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise RuntimeError("dev server did not start")

        with sync_playwright() as p:
            browser = p.chromium.launch(channel=channel, headless=True)
            page = browser.new_page(viewport=VIEWPORT, device_scale_factor=SCALE)

            def shot(caption: str, kind: str = "info", ms: int = 2600) -> None:
                img = Image.open(io.BytesIO(page.screenshot())).convert("RGB").resize(BROWSER_SIZE)
                tl.add(with_caption(img, caption, kind), ms)

            def settle() -> None:
                page.wait_for_load_state("load")
                page.wait_for_timeout(400)

            page.goto(base + "/", wait_until="load")
            settle()
            shot("Home: every book as a cover card, shuffled on each visit, with genre buttons")

            page.locator('a[href^="?genre="]').nth(1).click()
            settle()
            shot("Genre buttons narrow the shelf")

            page.locator("a:has(.book-card)").first.click()
            settle()
            shot("Book page: cover, author, year, genre and synopsis")

            page.locator("div.d-flex a.btn-sm").nth(1).click()
            settle()
            shot("Previous / next buttons step through the shelf")

            page.get_by_text("Login to Save Favourites").click()
            settle()
            page.fill('input[name="username"]', DEMO_USER)
            page.fill('input[name="password"]', password)
            shot("Log in (a throwaway demo account in a copy of the database)")
            page.click('button[type="submit"]')
            settle()

            page.locator("a:has(.book-card)").first.click()
            settle()
            shot("Logged in: favourite, add and delete controls appear", ms=2200)
            page.get_by_text("Add to Favourites").click()
            settle()
            shot("The heart toggles: saved to your favourites")

            page.goto(base + "/favourites/", wait_until="load")
            settle()
            shot("Favourites page lists only your saved books")

            page.goto(base + "/book/9999/", wait_until="load")
            settle()
            shot("A book that doesn't exist returns a 404 (checked by a test)", "bad", 2600)
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", default="chrome", help="installed browser for Playwright: chrome or msedge")
    args = ap.parse_args()
    password = secrets.token_urlsafe(12)

    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp) / "site"
        shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns("__pycache__", "docs", "venv", ".venv", ".git"))
        subprocess.run(
            [
                sys.executable, "manage.py", "shell", "-c",
                "from django.contrib.auth import get_user_model; "
                f"get_user_model().objects.create_user('{DEMO_USER}', password='{password}')",
            ],
            cwd=site, env=ENV, check=True, capture_output=True,
        )

        tl = Timeline()
        record_site(site, password, args.channel, tl)
        cmd = [sys.executable, "manage.py", "test"]
        tl.add_scenes(
            [
                Scene(
                    caption="9 tests: genre filter, login required, favourites toggle and privacy, prev/next and 404",
                    kind="good",
                    command="python manage.py test",
                    output=[l for l in run_merged(cmd, site) if l.strip()],
                    hold_ms=3500,
                )
            ],
            TITLE,
        )
        tl.save(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
