#!/usr/bin/env python3
"""Validate data/apps.json and verify every listed entry is genuinely alive.

Three levels of checking, because HTTP 200 alone is close to meaningless here:

1. Schema — required fields, categories, duplicates, description quality.
2. Reachability — the URL resolves at all.
3. Substance — for t.me links, whether the bot still EXISTS (Telegram serves a
   200 with a placeholder page for deleted bots, so a naive link checker will
   happily report a dead bot as fine); for github.com links, when the project
   was last pushed to, so abandoned repos get flagged rather than silently
   rotting in the list.

Run with --check-links to do 2 and 3. Without it, only the schema is checked,
which needs no network and is instant.
"""
import argparse
import concurrent.futures
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "apps.json"

REQUIRED = ("name", "url", "description", "category", "lastChecked", "status")
CATEGORIES = ("Products", "Games", "Open Source Projects", "Libraries & Templates")
UA = "Mozilla/5.0 (compatible; tma-catalog-linkcheck/1.0)"

MIN_DESC, MAX_DESC = 20, 400

# A GitHub project untouched for this long gets flagged. Not removed — plenty of
# small tools are simply finished — but a reader deserves to know.
STALE_DAYS = 365

# Telegram returns HTTP 200 for usernames that do not exist. These og:title
# values are what it serves instead of a real bot name. Established empirically
# against known-live and known-dead usernames, not guessed.
DEAD_TITLE_EXACT = {"Telegram – a new era of messaging", "Telegram"}
DEAD_TITLE_PREFIX = "Telegram: Contact @"


def load():
    try:
        return json.loads(DATA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"data/apps.json is not valid JSON: {exc}")


def validate(payload):
    problems = []
    apps = payload.get("apps")
    if not isinstance(apps, list) or not apps:
        sys.exit("data/apps.json must contain a non-empty 'apps' array")

    seen = {}
    for i, app in enumerate(apps):
        where = f"apps[{i}] ({app.get('name', 'unnamed')})"

        for field in REQUIRED:
            if not app.get(field):
                problems.append(f"{where}: missing required field '{field}'")

        url = app.get("url", "")
        if url and not url.startswith("https://"):
            problems.append(f"{where}: url must start with https://")

        key = url.lower().rstrip("/")
        if key in seen:
            problems.append(f"{where}: duplicate of {seen[key]}")
        seen[key] = where

        cat = app.get("category")
        if cat and cat not in CATEGORIES:
            problems.append(f"{where}: unknown category '{cat}' (allowed: {', '.join(CATEGORIES)})")

        desc = app.get("description", "")
        if desc:
            if len(desc) < MIN_DESC:
                problems.append(f"{where}: description is too short to be useful")
            if len(desc) > MAX_DESC:
                problems.append(f"{where}: description exceeds {MAX_DESC} characters")
            if not desc[0].isupper():
                problems.append(f"{where}: description should start with a capital letter")
            if not desc.rstrip().endswith("."):
                problems.append(f"{where}: description should end with a period")

    return problems


def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = b"" if method == "HEAD" else resp.read(200_000)
        return resp.status, body.decode("utf-8", "replace")


def og_title(html):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else ""


def check_telegram(url, html):
    """Return None if the bot looks alive, else a human-readable reason."""
    title = og_title(html)
    if not title:
        return "Telegram page has no title — the bot may no longer exist"
    if title in DEAD_TITLE_EXACT or title.startswith(DEAD_TITLE_PREFIX):
        return f"Telegram shows a placeholder page ('{title}') — the bot no longer exists"
    return None


def gh_pushed_at(url):
    """Last push date for a github.com/owner/repo URL, or None."""
    m = re.match(r"https://github\.com/([^/]+)/([^/?#]+)", url)
    if not m:
        return None
    api = f"https://api.github.com/repos/{m.group(1)}/{m.group(2).removesuffix('.git')}"
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    # Use the Actions token when present — unauthenticated API is rate-limited
    # to 60/hour, which a weekly run over a growing list would exhaust.
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(api, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read()).get("pushed_at")
    except Exception:  # noqa: BLE001 — a rate limit or a private repo is not fatal
        return None


def probe(app):
    """Returns (app, status_label, note). status_label is ok/unreachable/missing."""
    url = app["url"]
    host = urllib.parse.urlparse(url).netloc.lower()

    html = ""
    try:
        status, html = fetch(url)
    except urllib.error.HTTPError as exc:
        return app, "unreachable", f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return app, "unreachable", f"{type(exc).__name__}: {exc}"

    if not 200 <= status < 400:
        return app, "unreachable", f"HTTP {status}"

    if host in ("t.me", "telegram.me"):
        reason = check_telegram(url, html)
        if reason:
            return app, "missing", reason

    note = None
    if host == "github.com":
        pushed = gh_pushed_at(url)
        if pushed:
            app["lastCommit"] = pushed[:10]
            age = (datetime.date.today() - datetime.date.fromisoformat(pushed[:10])).days
            app["staleDays"] = age
            if age > STALE_DAYS:
                note = f"no commits in {age // 30} months"
        # A repo we cannot query keeps whatever it had; absence of data is not
        # evidence of abandonment.

    return app, "ok", note


def check_links(payload):
    apps = payload["apps"]
    today = datetime.date.today().isoformat()
    broken, stale = [], []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for app, status, note in pool.map(probe, apps):
            app["status"] = status
            app["lastChecked"] = today
            if status == "ok":
                app.pop("statusReason", None)
                if note:
                    app["staleNote"] = note
                    stale.append(f"{app['name']}: {note}")
                else:
                    app.pop("staleNote", None)
            else:
                app["statusReason"] = note or status
                broken.append(f"{app['name']} -> {app['url']} ({note or status})")

    payload["updated"] = today
    DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return broken, stale


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-links", action="store_true",
                        help="verify every URL, detect deleted bots and abandoned repos")
    args = parser.parse_args()

    payload = load()
    problems = validate(payload)
    if problems:
        print("Schema problems:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    print(f"Schema OK — {len(payload['apps'])} entries.")

    if args.check_links:
        broken, stale = check_links(payload)
        if stale:
            print(f"\n{len(stale)} entries flagged as inactive (listed, not removed):")
            for s in stale:
                print(f"  - {s}")
        if broken:
            print("\nBroken or missing entries:", file=sys.stderr)
            for b in broken:
                print(f"  - {b}", file=sys.stderr)
            sys.exit(1)
        print(f"\nAll {len(payload['apps'])} entries resolve and still exist.")


if __name__ == "__main__":
    main()
