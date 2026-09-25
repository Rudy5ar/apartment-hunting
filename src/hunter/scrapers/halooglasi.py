import html
import json
import re

from bs4 import BeautifulSoup

from hunter.config import Config
from hunter.http import get_text
from hunter.listing import Listing
from hunter.scrapers.fourzida import fold_city

_PRICE = re.compile(r'data-value="(\d+)"')
_ROOMS = re.compile(r"(\d+(?:[.,]\d+)?)\s*Broj soba", re.I)


def _structure(title: str, rooms: str) -> str:
    low = title.lower()
    if "garsonjera" in low or rooms in ("0.5", "0,5"):
        return "garsonjera"
    if "jednoiposoban" in low or rooms in ("1.5", "1,5"):
        return "jednoiposoban"
    if "jednosoban" in low or rooms in ("1", "1.0", "1,0"):
        return "jednosoban"
    return ""


def search(cfg: Config) -> list[Listing]:
    city = fold_city(cfg.filters.city)
    max_rent = int(cfg.filters.max_rent_eur)
    listings: list[Listing] = []
    seen: set[str] = set()
    for structure in cfg.filters.structures:
        url = (
            f"https://www.halooglasi.com/nekretnine/izdavanje-stanova/{city}/{structure}"
            f"?cena_d_from=0&cena_d_to={max_rent}&cena_d_unit=4"
        )
        for item in _search_page(get_text(url), cfg):
            if item.id in seen:
                continue
            seen.add(item.id)
            listings.append(item)
    return listings


def _search_page(page: str, cfg: Config) -> list[Listing]:
    idx = page.find('"Ads":')
    if idx < 0:
        raise RuntimeError("halooglasi.com did not include Ads JSON (possible block)")
    ads, _ = json.JSONDecoder().raw_decode(page, idx + len('"Ads":'))
    listings: list[Listing] = []
    for ad in ads:
        card = html.unescape(ad.get("ListHTML") or "")
        text = BeautifulSoup(card, "html.parser").get_text(" ", strip=True)
        price_match = _PRICE.search(card)
        rooms_match = _ROOMS.search(text)
        rooms = rooms_match.group(1).replace(",", ".") if rooms_match else ""
        title = str(ad.get("Title") or "")
        description = str(ad.get("Text") or "")
        relative = str(ad.get("RelativeUrl") or "").split("?")[0]
        link = "https://www.halooglasi.com" + relative
        phone = ad.get("PhoneNumber1") or ad.get("PhoneNumber2") or ""
        listings.append(
            Listing(
                site="halooglasi",
                id=str(ad.get("Id") or relative),
                url=link,
                price_eur=float(price_match.group(1)) if price_match else None,
                structure=_structure(title + " " + text, rooms),
                city=cfg.filters.city,
                text=f"{cfg.filters.city} {title} {text} {description}",
                address=title,
                phone=re.sub(r"\s+", "", str(phone)) if phone else "",
            )
        )
    return listings


def enrich(listing: Listing) -> Listing:
    page = get_text(listing.url)
    soup = BeautifulSoup(page, "html.parser")
    listing.text += "\n" + soup.get_text(" ", strip=True)[:12000]
    if not listing.phone:
        found = re.search(r"\+381[\d\s/\-]{6,16}|06\d[\d\s/\-]{6,14}", listing.text)
        if found:
            listing.phone = re.sub(r"[\s/\-]", "", found.group(0))
    return listing
