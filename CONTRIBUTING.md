# Adding your app

**The promise: your pull request gets a decision within 7 days.** Not a merge
necessarily — a decision. If it is rejected you will be told why, in a sentence,
so you can fix it and resubmit.

That promise exists because this catalog was started after watching perfectly
good submissions sit unanswered elsewhere for over a year.

## What to edit

Edit **`data/apps.json` only.** Do not touch `README.md` or `llms.txt` — both are
generated from the JSON, and any hand-edit there will be overwritten on the next
build.

Add one object to the `apps` array:

```json
{
  "name": "Your App",
  "url": "https://t.me/your_bot",
  "description": "What it does, in one or two plain sentences.",
  "category": "Products",
  "contributedBy": "your-github-username",
  "lastChecked": "2026-07-31",
  "status": "ok"
}
```

## Rules

- **`category`** must be one of: `Products`, `Games`, `Open Source Projects`,
  `Libraries & Templates`.
- **`url`** must be `https://` and must load. CI checks this on every pull
  request, so a dead link fails before a human ever looks at it.
- **`description`** — 20 to 400 characters, starts with a capital, ends with a
  period. Write what the app actually does. Not "the best revolutionary
  platform" — what it does.
- **One app per pull request.** Two apps, two pull requests.
- **No duplicates.** CI checks the URL against everything already listed.

## What gets rejected

- Anything that does not load, or that needs a payment before it does anything.
- Descriptions that are marketing copy rather than a description. If a reader
  cannot tell what your app does after reading it, it is not a description.
- Apps that promise something they cannot deliver. In this ecosystem that
  usually means claiming access to private data on some other platform.
- Bulk submissions of near-identical apps from one author.

## Running the checks locally

```bash
python3 scripts/check.py               # schema only, instant
python3 scripts/check.py --check-links # also verifies every URL
python3 scripts/build.py               # regenerate README.md and llms.txt
```

No dependencies beyond the Python standard library — nothing to install.

## Removing your app

Open an issue saying so. It comes out, no questions asked. This applies
especially to entries carried over from the older unmerged pull requests: if
that was not what you wanted, say the word.
