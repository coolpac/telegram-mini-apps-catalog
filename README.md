# Telegram Mini Apps — a catalog that is actually maintained

Every entry is re-checked automatically every week. Not just "does the URL
return 200" — for Telegram links the check confirms the bot still **exists**
(Telegram serves a normal 200 page for deleted bots, so naive link checkers
report them as healthy), and for GitHub links it reports how long the project
has been untouched.

**Submissions get a decision within 7 days.** See [CONTRIBUTING.md](CONTRIBUTING.md).

- **29 apps**, last verified **2026-08-03**
- **3** flagged as inactive — listed, but marked, not quietly left to rot
- Machine-readable copy: [`data/apps.json`](data/apps.json)
- Every entry records who contributed it and when it was last checked

## Contents

- [Products](#products)
- [Games](#games)
- [Open Source Projects](#open-source-projects)
- [Libraries & Templates](#libraries-templates)


## Products

- [Appla](https://t.me/ApplaFableBot) - No-code builder for business Mini Apps: QR menu, online booking, loyalty card. 12 languages, free preview, publish with Stars.
- [Apps Father](https://apps-father.com) - AI builder to create, publish, and update Telegram Mini Apps from a plain-text description, with built-in Telegram Stars and TON payments.
- [BookClass](https://t.me/BookClassBot) - Class booking Mini App for studios, trainers, and instructors of any kind.
- [Daily Tarot](https://t.me/thisisthedailytarotbot) - Daily tarot card pull with Mini App, Rider-Waite deck (public domain), 7 languages, Telegram Stars payments.
- [DefyTON](https://t.me/DefyTONBot/app) - AI-verified habit challenges with GRAM staking and TON Connect integration.
- [EventEdge](https://t.me/polym_lab_bot) - Backtest and paper-trade strategies on prediction markets (Polymarket, Manifold, Kalshi) with no code and no wallet connection.
- [Gategram](https://gategram.app) - Sell digital content on Telegram with native Stars payments. Open-source, 95% creator earnings.
- [Invoice Generator](https://t.me/freelance_inv_bot) - Create and send professional invoices to clients directly inside Telegram.
- [Lexicon](https://t.me/lexicon_snap_bot?startapp=cat_awesome) - Flashcards for memorizing foreign words: own decks by language pair, auto-translate suggestions, streaks and reminders. Pixel-art UI, EN/RU/PT/ES/FR.
- [SocialHub](https://t.me/SocialHubGlobal_bot/app) - Web3 social media platform where every interaction earns real USDT directly to your wallet.
- [StoriesFly](https://t.me/instanavy_bot) - View public Instagram stories anonymously, download media in HD, and track follower and unfollower changes with alerts inside Telegram. Public accounts only, 20 languages.
- [YupSoul](https://t.me/Yup_Soul_bot) - A music oracle: a personal song from your birth date, plus a daily AI oracle chat.
- [Zodiac Info](https://t.me/zodiac_info_bot) - Daily horoscopes, numerology, and moon day insights. Free to use, with full EN/RU localization.

## Games

- [Arena Defense](https://t.me/arena_defense_bot/arena_defense) - Idle auto-battler defense: build a party of 10 heroes, unleash screen-clearing skills, and hold the line across 10 chapters. Playable in EN/KO/RU/ZH.
- [Catallaxy](https://t.me/catallaxy_bot) - Marketplace for digital goods paid in GRAM or USDT — gift cards, game top-ups, Telegram Stars and Premium, per-message AI, and TON utilities, with instant in-browser delivery. [Site](https://ctlx.cc) also available.
- [CrazyWorld](https://t.me/CrazyWorld_GameBot) - Real-time strategy where clans fight over the real world map cell by cell, with paratroopers, drones, nukes, base-building and 2-week seasons.
- [Feline Dynasty](https://t.me/FelineDynastyBot) - Idle cat-breeding game on TON: collect and breed NFT cats, grow your habitat and earn rewards, with a marketplace, guilds and DeFi.
- [KeyFire Games](https://keyfire.github.io/games/) - Ten casual Telegram mini games (2048, Sudoku, Klondike, Bubble Pop, Backgammon and more) in five languages.
- [Playful Mind](https://t.me/playful_mind_bot/play?startapp=cat_awesome_tma) - A small collection of calm brain games (memory & logic) — a few quiet minutes a day, free, no ads.
- [Rignite](https://t.me/RigniteBot) - A mining tap-to-earn game where you mine RGT and withdraw RGNT, a real TON jetton tradable on STON.fi.
- [Squad Signal](https://t.me/squad_signal_bot) - Daily prediction game: call crypto moves and meme trends before they happen. Flash rounds, squad leaderboards, Telegram Stars rewards.

## Open Source Projects

- [Cosmic Bugs](https://github.com/keyfire/fresh-space-invaders) - A dependency-free, single-file HTML5 Canvas arcade shooter (Space Invaders style) with power-ups, bosses, and RU/EN/ES/PT/TR localization.
- [CSUBOT](https://github.com/cjh0613/csubot) - Telegram Web APP CAPTCHA Bot to verify if incoming group users are real humans.  *(no commits in 14 months)*
- [MemoCard](https://github.com/kubk/memo-card) - Flashcard app for improving memory with spaced repetition.
- [NobleTruths](https://github.com/MaximStone/eight-truths) - Habit daily journal for practitioners.  *(no commits in 17 months)*
- [OpenFreeMap](https://github.com/asan-pf/tma-ofm-react-template) - Share and discover locations with telegram and OpenFreeMaps.

## Libraries & Templates

- [Authentication using TMA using nestJS and NextJS](https://github.com/e3ob/Telegram-Mini-App-Auth) - Template for authentication in a Telegram Mini App using NestJS.  *(no commits in 15 months)*
- [twa-nextjs-monorepo-starter](https://github.com/eugeneshilow/twa-nextjs-monorepo-starter) - Starter template for Telegram Mini Apps using Next.js in a pnpm monorepo.
- [Types for Telegram Web Apps (TWA) SDK](https://github.com/fullpipe/twa-sdk-types) - Types for Telegram Web Apps (TWA) SDK. Fast updates.

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
