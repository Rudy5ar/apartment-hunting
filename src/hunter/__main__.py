import logging
import os
import time

from hunter.config import load_config, load_env
from hunter.filters import amenity_match, hard_match
from hunter.notify import format_listing, send
from hunter.scrapers import ENRICH, SCRAPERS
from hunter.store import Store

log = logging.getLogger("hunter")


def poll_once(cfg, store: Store, token: str, chat_id: str) -> None:
    for site in cfg.sites:
        if not site.enabled:
            continue
        search = SCRAPERS.get(site.id)
        if search is None:
            log.error("no scraper registered for %s", site.id)
            continue
        try:
            found = search(cfg)
        except Exception:
            log.exception("scrape failed for %s", site.id)
            continue
        baseline = not store.is_ready(site.id)
        matches = []
        for listing in found:
            if store.seen(site.id, listing.id):
                continue
            if not hard_match(listing, cfg.filters):
                continue
            if not amenity_match(listing, cfg.filters):
                try:
                    listing = ENRICH[site.id](listing)
                except Exception:
                    log.exception("detail fetch failed for %s %s", site.id, listing.id)
                    continue
            matched = amenity_match(listing, cfg.filters)
            if not matched:
                continue
            if baseline:
                store.mark(site.id, listing.id)
                matches.append(listing)
                continue
            try:
                send(token, chat_id, format_listing(listing, cfg.filters.neighborhoods))
            except Exception:
                log.exception("telegram failed for %s %s", site.id, listing.id)
                continue
            store.mark(site.id, listing.id)
            log.info("notified %s %s", site.id, listing.id)
        if baseline:
            try:
                send(
                    token,
                    chat_id,
                    f"{site.id} baseline: {len(matches)} existing matches saved, not pinging them. Watching for new ones.",
                )
            except Exception:
                log.exception("baseline telegram failed for %s", site.id)
                continue
            store.set_ready(site.id)
            log.info("%s baseline saved %s matches", site.id, len(matches))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    load_env()
    cfg = load_config()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
    store = Store()
    while True:
        try:
            poll_once(cfg, store, token, chat_id)
        except Exception:
            log.exception("poll failed")
        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    main()
