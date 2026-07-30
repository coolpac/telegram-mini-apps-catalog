#!/usr/bin/env python3
"""Validate data/apps.json and verify every listed URL still resolves.

Run with --check-links to actually hit the network (used by the weekly job and
by pull-request CI). Without it, only the schema is validated, which is fast
enough to run on every commit.

Exit code is non-zero if anything is wrong, so CI fails loudly rather than
silently publishing a list full of dead links.
"""
import argparse
import concurrent.futures
import datetime
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "apps.json"

REQUIRED = ("name", "url", "description", "category", "lastChecked", "status")
CATEGORIES = ("Products", "Games", "Open Source Projects", "Libraries & Templates")
UA = "Mozilla/5.0 (compatible; tma-catalog-linkcheck/1.0)"

# Descriptions are contributor-written. We keep them as-is, but they have to be
# a real sentence rather than a marketing fragment or a wall of keywords.
MIN_DESC = 20
MAX_DESC = 400


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
        if url and not re.match(r"^https://", url):
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


def probe(app):
    """Return (app, http_status_or_error). Follows redirects, HEAD then GET."""
    url = app["url"]
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return app, resp.status
        except urllib.error.HTTPError as exc:
            # Some hosts reject HEAD but serve GET perfectly well.
            if method == "HEAD":
                continue
            return app, exc.code
        except Exception as exc:  # noqa: BLE001 - network errors are all equal here
            if method == "HEAD":
                continue
            return app, f"{type(exc).__name__}: {exc}"
    return app, "unreachable"


def check_links(payload):
    apps = payload["apps"]
    today = datetime.date.today().isoformat()
    dead = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for app, status in pool.map(probe, apps):
            ok = isinstance(status, int) and 200 <= status < 400
            app["status"] = "ok" if ok else "unreachable"
            app["lastChecked"] = today
            if not ok:
                dead.append(f"{app['name']} -> {app['url']} ({status})")

    payload["updated"] = today
    DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dead


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-links", action="store_true",
                        help="also verify every URL over the network")
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
        dead = check_links(payload)
        if dead:
            print("Unreachable entries:", file=sys.stderr)
            for d in dead:
                print(f"  - {d}", file=sys.stderr)
            sys.exit(1)
        print("All links reachable.")


if __name__ == "__main__":
    main()
