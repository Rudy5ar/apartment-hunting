# Apartment hunter

Polls 4zida, Halo oglasi, Nekretnine.rs, and City Expert for new Novi Sad rentals and sends a Telegram message when a listing matches `config.yaml`.

Current filters: jednosoban, up to 350 EUR, Grbavica / Liman 3 / Liman 4, and the listing text must mention klima and optika. Edit `config.yaml` to change them. Turn a site off with `enabled: false`. A new site is a module in `src/hunter/scrapers/` plus one line in `config.yaml` and the registry in `src/hunter/scrapers/__init__.py`.

The first successful poll of each site saves current matches and sends one baseline message. Later polls message only new matches. Seen ids live in `data/seen.db`.

Nekretnine.rs sometimes answers with a captcha. That site is skipped for the cycle; the others keep running. A home connection is the reliable place to run this.

## Telegram

1. Message [@BotFather](https://t.me/BotFather), create a bot, copy the token.
2. Message your bot once.
3. Open `https://api.telegram.org/bot<token>/getUpdates` and copy the `chat.id`.
4. Copy `.env.example` to `.env` and fill both values.

## Run locally

```bash
pip install -e .
python -m hunter
```

## Run in a container

```bash
docker compose up -d
```

`config.yaml` and `data/` are mounted, so filter edits and seen listings survive restarts. Poll interval defaults to 45 seconds.
