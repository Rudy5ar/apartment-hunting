# Apartment hunter

Polls 4zida, Halo oglasi, and City Expert and sends a Telegram message when a listing matches `config.yaml`.

Filters, poll interval, and which sites run are all set in `config.yaml`: `city`, `structures`, `max_rent_eur`, `neighborhoods`, optional `required` words the listing text must contain, `poll_seconds`, and `enabled` per site. Turn a site off with `enabled: false`. A new site is a module in `src/hunter/scrapers/` plus one line in `config.yaml` and the registry in `src/hunter/scrapers/__init__.py`.

The first successful poll of each site saves current matches and sends one baseline message. Later polls message only new matches. Seen ids live in `data/seen.db`.

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
