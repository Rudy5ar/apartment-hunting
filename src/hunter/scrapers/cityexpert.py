import json
import re

from bs4 import BeautifulSoup

from hunter.config import Config
from hunter.http import get_text
from hunter.listing import Listing
from hunter.scrapers.fourzida import fold_city

_STRUCTURES = {
    "0.5": "garsonjera",
    "1.0": "jednosoban",
    "1": "jednosoban",
    "1.5": "jednoiposoban",
    "2.0": "dvosoban",
}
_AMENITY = {"furaircon": "klima", "furinverter": "klima"}
_PHONE = re.compile(r"\+381[\d\s/\-]{6,16}|06\d[\d\s/\-]{6,14}")


def _result_list(html: str) -> list[dict]:
    match = re.search(
        r'<script id="ng-state" type="application/json">(.*?)</script>', html, re.S
    )
    if not match:
        raise RuntimeError("cityexpert.rs did not include ng-state JSON")
    data = json.loads(match.group(1))
    for value in data.values():
        body = value.get("b") if isinstance(value, dict) else None
        result = body.get("result") if isinstance(body, dict) else None
        if isinstance(result, list) and result and isinstance(result[0], dict):
            if "propId" in result[0]:
                return result
    raise RuntimeError("cityexpert.rs JSON had no listing results")


def search(cfg: Config) -> list[Listing]:
    city = fold_city(cfg.filters.city)
    html = get_text(f"https://cityexpert.rs/izdavanje-nekretnina/{city}")
    listings: list[Listing] = []
    for item in _result_list(html):
        prop_id = str(item.get("propId"))
        polygons = [str(part) for part in item.get("polygons") or []]
        furnishing = [str(part) for part in item.get("furnishingArray") or []]
        amenity_words = [
            _AMENITY[part.lower()] for part in furnishing if part.lower() in _AMENITY
        ]
        street = str(item.get("street") or "")
        structure = _STRUCTURES.get(str(item.get("structure")), "")
        listings.append(
            Listing(
                site="cityexpert",
                id=prop_id,
                url=f"https://cityexpert.rs/izdavanje-nekretnina/{city}/{prop_id}",
                price_eur=float(item["price"]) if item.get("price") is not None else None,
                structure=structure,
                city=cfg.filters.city,
                text=" ".join([cfg.filters.city, street, *polygons, *amenity_words, *furnishing]),
                address=street,
            )
        )
    return listings


def enrich(listing: Listing) -> Listing:
    html = get_text(listing.url)
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    listing.text += "\n" + text[:12000]
    if not listing.phone:
        found = _PHONE.search(text)
        if found:
            listing.phone = re.sub(r"[\s/\-]", "", found.group(0))
    return listing
