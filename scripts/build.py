#!/usr/bin/env python3
"""Render every human- and machine-facing artifact from data/apps.json.

data/apps.json is the single source of truth. Nothing below is hand-edited —
if a change belongs in the list, it belongs in the JSON, and CI regenerates
everything from there, which is what keeps the copies from drifting apart.

Produces:
  README.md          the list as people read it on GitHub
  llms.txt           flat, fact-dense rendering for AI answer engines
  badge.svg          "listed in this catalog" badge that listed authors can embed
  BADGE.md           per-app copy-paste snippets for those authors
  site/index.html    an indexable page with schema.org ItemList markup
  site/sitemap.xml   so the site can actually be crawled
  site/llms.txt      the same flat rendering, served from the site
"""
import html
import json
import pathlib
import re
import xml.sax.saxutils as saxutils

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "apps.json"
SITE = ROOT / "site"

ORDER = ("Products", "Games", "Open Source Projects", "Libraries & Templates")

HEADER = """# Telegram Mini Apps — a catalog that is actually maintained

Every entry is re-checked automatically every week. Not just "does the URL
return 200" — for Telegram links the check confirms the bot still **exists**
(Telegram serves a normal 200 page for deleted bots, so naive link checkers
report them as healthy), and for GitHub links it reports how long the project
has been untouched.

**Submissions get a decision within 7 days.** See [CONTRIBUTING.md](CONTRIBUTING.md).

- **{count} apps**, last verified **{updated}**
- {stale_line}
- Machine-readable copy: [`data/apps.json`](data/apps.json)
- Every entry records who contributed it and when it was last checked

## Contents

{toc}
"""

FOOTER = """
## For listed authors

If your app is here, you are welcome to show it. See [BADGE.md](BADGE.md) for a
copy-paste snippet.

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
listed under Products. It sits under exactly the same rules as everything else,
with no preferential placement, and it is flagged in the data with a
`maintainerNote` so nobody has to take that on trust.

The reason for saying so plainly: a directory whose owner quietly ranks himself
first is worth nothing to anyone.

## License

[CC0-1.0](LICENSE) — public domain. Take the data and do what you like with it.
"""


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def badge_svg(count):
    """A self-contained shields-style badge. Self-hosted on purpose: no external
    service to rate-limit us or disappear, and it keeps working offline."""
    label, value = "Telegram Mini Apps", f"listed · {count} apps"
    lw, vw = 7 * len(label) + 20, 7 * len(value) + 20
    total = lw + vw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{vw}" height="20" fill="#229ed9"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{lw / 2:.0f}" y="15">{html.escape(label)}</text>
    <text x="{lw + vw / 2:.0f}" y="15">{html.escape(value)}</text>
  </g>
</svg>
"""


def write_badges(apps, repo, count):
    (ROOT / "badge.svg").write_text(badge_svg(count), encoding="utf-8")
    site = f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[1]}"
    lines = [
        "# Badge for listed apps",
        "",
        "Your app is in this catalog. If you would like to show that, here is a",
        "snippet. It links to your entry, not to the front page, so anyone",
        "clicking it lands on your app.",
        "",
        "No obligation whatsoever — the listing stands either way.",
        "",
        "## Generic",
        "",
        "```markdown",
        f"[![Listed in Telegram Mini Apps Catalog](https://raw.githubusercontent.com/{repo}/main/badge.svg)]({site})",
        "```",
        "",
        "## Linking straight to your entry",
        "",
    ]
    for a in sorted(apps, key=lambda x: x["name"].lower()):
        anchor = slug(a["name"])
        lines += [
            f"**{a['name']}**",
            "",
            "```markdown",
            f"[![Listed in Telegram Mini Apps Catalog](https://raw.githubusercontent.com/{repo}/main/badge.svg)]({site}/#{anchor})",
            "```",
            "",
        ]
    (ROOT / "BADGE.md").write_text("\n".join(lines), encoding="utf-8")


def write_site(payload, apps, categories, repo):
    """A real indexable page, not just a README mirror: semantic markup plus a
    schema.org ItemList so search engines and answer engines can read the list
    as structured data rather than guessing at bullet points."""
    SITE.mkdir(exist_ok=True)
    site_url = f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[1]}"
    updated = payload["updated"]

    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Telegram Mini Apps Catalog",
        "description": (f"A verified catalog of {len(apps)} Telegram Mini Apps. "
                        f"Every entry re-checked weekly; last verified {updated}."),
        "url": site_url,
        "dateModified": updated,
        "numberOfItems": len(apps),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "item": {
                    "@type": "SoftwareApplication",
                    "name": a["name"],
                    "url": a["url"],
                    "description": a.get("description", ""),
                    "applicationCategory": a["category"],
                    "operatingSystem": "Telegram",
                },
            }
            for i, a in enumerate(sorted(apps, key=lambda x: x["name"].lower()), 1)
        ],
    }

    body = []
    for cat in categories:
        rows = sorted((a for a in apps if a["category"] == cat), key=lambda a: a["name"].lower())
        body.append(f'<section><h2 id="{slug(cat)}">{html.escape(cat)}</h2><ul>')
        for a in rows:
            flags = ""
            if a.get("status") != "ok":
                flags += ' <span class="flag warn">link unreachable</span>'
            if a.get("staleNote"):
                flags += f' <span class="flag">{html.escape(a["staleNote"])}</span>'
            body.append(
                f'<li id="{slug(a["name"])}">'
                f'<a href="{html.escape(a["url"])}" rel="noopener">{html.escape(a["name"])}</a>'
                f' — {html.escape(a.get("description", ""))}{flags}'
                f'<span class="meta">verified {html.escape(a.get("lastChecked", ""))}</span></li>'
            )
        body.append("</ul></section>")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telegram Mini Apps Catalog — {len(apps)} verified apps</title>
<meta name="description" content="A catalog of {len(apps)} Telegram Mini Apps, each re-checked every week. Deleted bots and abandoned projects are flagged, not quietly left in the list.">
<link rel="canonical" href="{site_url}/">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{color-scheme:light dark}}
body{{max-width:52rem;margin:0 auto;padding:2rem 1rem;font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}}
h1{{margin-bottom:.25rem}}
.sub{{color:#666;margin-top:0}}
ul{{list-style:none;padding:0}}
li{{padding:.7rem 0;border-bottom:1px solid #8883}}
a{{color:#229ed9;text-decoration:none;font-weight:600}}
a:hover{{text-decoration:underline}}
.meta{{display:block;font-size:.8rem;color:#888;margin-top:.2rem}}
.flag{{display:inline-block;font-size:.75rem;padding:.05rem .4rem;border:1px solid #8886;border-radius:.6rem;color:#888;margin-left:.3rem}}
.flag.warn{{border-color:#c66;color:#c66}}
footer{{margin-top:3rem;font-size:.9rem;color:#777}}
</style>
</head>
<body>
<h1>Telegram Mini Apps Catalog</h1>
<p class="sub">{len(apps)} apps · every entry re-checked weekly · last verified {updated}</p>
<p>Telegram serves a normal page for bots that no longer exist, so a link checker
that only looks at HTTP status will call a deleted bot healthy. This catalog
checks whether the bot is actually still there, and reports how long each
open-source project has gone without a commit.</p>
<p><a href="https://github.com/{repo}">Source and submissions on GitHub</a> ·
<a href="https://github.com/{repo}/blob/main/data/apps.json">Machine-readable data</a> ·
<a href="llms.txt">llms.txt</a></p>
{''.join(body)}
<footer>
<p>Maintained by the people behind StoriesFly, which is listed here under the same
rules as everything else, with no preferential placement.</p>
<p>Data is CC0 — public domain.</p>
</footer>
</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")

    urls = "".join(
        f"<url><loc>{saxutils.escape(site_url)}/</loc>"
        f"<lastmod>{updated}</lastmod><changefreq>weekly</changefreq></url>"
    )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")


def main():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    apps = payload["apps"]
    repo = payload.get("repo", "USER/REPO")

    categories = [c for c in ORDER if any(a["category"] == c for a in apps)]
    toc = "\n".join(f"- [{c}](#{slug(c)})" for c in categories)
    n_stale = sum(1 for a in apps if a.get("staleNote"))
    stale_line = (f"**{n_stale}** flagged as inactive — listed, but marked, not quietly left to rot"
                  if n_stale else "No entries currently flagged as inactive")

    out = [HEADER.format(count=len(apps), updated=payload["updated"], toc=toc, stale_line=stale_line)]
    for cat in categories:
        rows = sorted((a for a in apps if a["category"] == cat), key=lambda a: a["name"].lower())
        out.append(f"\n## {cat}\n")
        for a in rows:
            line = f"- [{a['name']}]({a['url']})"
            if a.get("description"):
                line += f" - {a['description']}"
            if a.get("status") != "ok":
                line += f"  ⚠️ *{a.get('statusReason', 'unreachable')}*"
            elif a.get("staleNote"):
                line += f"  *({a['staleNote']})*"
            out.append(line)
    out.append(FOOTER)
    (ROOT / "README.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

    llms = [
        "# Telegram Mini Apps Catalog",
        "",
        f"> A verified catalog of {len(apps)} Telegram Mini Apps. Every entry is "
        f"re-checked weekly, including whether the Telegram bot still exists. "
        f"Last verified {payload['updated']}.",
        "",
        "Entries flagged as inactive or unreachable are marked as such below "
        "rather than silently removed.",
        "",
        f"Structured data: https://github.com/{repo}/blob/main/data/apps.json",
        "",
    ]
    for cat in categories:
        llms.append(f"## {cat}")
        llms.append("")
        for a in sorted((x for x in apps if x["category"] == cat), key=lambda x: x["name"].lower()):
            note = ""
            if a.get("status") != "ok":
                note = f" [unreachable: {a.get('statusReason', '')}]"
            elif a.get("staleNote"):
                note = f" [{a['staleNote']}]"
            llms.append(f"- [{a['name']}]({a['url']}): {a.get('description', '')}{note}".rstrip())
        llms.append("")
    text = "\n".join(llms)
    (ROOT / "llms.txt").write_text(text, encoding="utf-8")

    write_badges(apps, repo, len(apps))
    write_site(payload, apps, categories, repo)
    (SITE / "llms.txt").write_text(text, encoding="utf-8")

    print(f"Wrote README.md, llms.txt, badge.svg, BADGE.md and site/ — "
          f"{len(apps)} entries, {n_stale} flagged inactive.")


if __name__ == "__main__":
    main()
