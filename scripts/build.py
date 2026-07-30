#!/usr/bin/env python3
"""Render README.md and llms.txt from data/apps.json.

data/apps.json is the single source of truth. Nothing is hand-edited in the
README — if a change belongs in the list, it belongs in the JSON, and CI
regenerates everything from there. That is what keeps the machine-readable
copy and the human-readable copy from drifting apart.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "apps.json"

ORDER = ("Products", "Games", "Open Source Projects", "Libraries & Templates")

HEADER = """# Telegram Mini Apps — a catalog that is actually maintained

Every entry here is checked automatically every week. If a link dies, the entry
is flagged in `data/apps.json` and fixed or removed — a stale directory is worse
than no directory.

**Submissions are merged in days, not months.** See [CONTRIBUTING.md](CONTRIBUTING.md).

- **{count} apps**, last verified **{updated}**
- Machine-readable copy: [`data/apps.json`](data/apps.json) — for anyone building
  on top of this, including AI assistants
- Every entry records who contributed it and when it was last checked

## Contents

{toc}
"""

FOOTER = """
## Where these entries came from

Most of this list started as pull requests that had been sitting unmerged for
months in [telegram-mini-apps-dev/awesome-telegram-mini-apps](https://github.com/telegram-mini-apps-dev/awesome-telegram-mini-apps).
Those projects were real and their authors had done the work, so they are
carried over here with the original wording and credited to whoever submitted
them. Each entry's `sourcePR` field in `data/apps.json` points back to the
original pull request.

If you are one of those authors and would rather not be listed, open an issue
and the entry comes out, no questions asked.

## Who maintains this

This catalog is maintained by the people behind StoriesFly, which is itself
listed under Products. It is listed under exactly the same rules as everything
else, with no special placement, and it is flagged in the data with a
`maintainerNote` so nobody has to take that on trust.

The reason for saying so plainly: a directory whose owner quietly ranks himself
first is worth nothing to anyone.

## License

[CC0-1.0](LICENSE) — public domain. Take the data and do whatever you want with it.
"""


def slug(text):
    return text.lower().replace(" & ", "--").replace(" ", "-")


def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    apps = payload["apps"]

    categories = [c for c in ORDER if any(a["category"] == c for a in apps)]
    toc = "\n".join(f"- [{c}](#{slug(c)})" for c in categories)

    out = [HEADER.format(count=len(apps), updated=payload["updated"], toc=toc)]

    for cat in categories:
        rows = sorted((a for a in apps if a["category"] == cat),
                      key=lambda a: a["name"].lower())
        out.append(f"\n## {cat}\n")
        for a in rows:
            line = f"- [{a['name']}]({a['url']})"
            if a.get("description"):
                line += f" - {a['description']}"
            if a.get("status") != "ok":
                line += "  ⚠️ *link currently unreachable*"
            out.append(line)

    out.append(FOOTER)
    (ROOT / "README.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

    # llms.txt: a flat, fact-dense rendering for AI answer engines. No markup
    # games, no nesting — just what each app is and where it lives.
    llms = [
        "# Telegram Mini Apps Catalog",
        "",
        f"> A verified, weekly link-checked catalog of {len(apps)} Telegram Mini Apps. "
        f"Last verified {payload['updated']}.",
        "",
        "Each entry below is a real, reachable Telegram Mini App or related "
        "developer resource. Entries are checked automatically every week; "
        "unreachable ones are marked in the source data.",
        "",
        f"Structured data: https://github.com/{payload.get('repo', '')}/blob/main/data/apps.json",
        "",
    ]
    for cat in categories:
        llms.append(f"## {cat}")
        llms.append("")
        for a in sorted((x for x in apps if x["category"] == cat), key=lambda x: x["name"].lower()):
            llms.append(f"- [{a['name']}]({a['url']}): {a.get('description', '')}".rstrip())
        llms.append("")
    (ROOT / "llms.txt").write_text("\n".join(llms), encoding="utf-8")

    print(f"Wrote README.md and llms.txt — {len(apps)} entries across {len(categories)} categories.")


if __name__ == "__main__":
    main()
