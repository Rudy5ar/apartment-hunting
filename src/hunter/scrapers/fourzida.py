import json
import re

from bs4 import BeautifulSoup

from hunter.config import Config
from hunter.http import get_text
from hunter.listing import Listing

_LDJSON = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.S
)
_PHONE = re.compile(r"\+381[\d\s/\-]{6,16}|06\d[\d\s/\-]{6,14}")


def fold_city(city: str) -> str:
    return (
        city.lower()
        .replace("č", "c")
        .replace("ć", "c")
        .replace("š", "s")
        .replace("ž", "z")
        .replace("đ", "dj")
        .replace(" ", "-")
    )


_STRUCTURES = {
    "jednosoban": "jednosoban",
    "jednoiposoban": "jednoiposoban",
    "garsonjera": "garsonjera",
    "dvosoban": "dvosoban",
    "dvoiposoban": "dvoiposoban",
    "trosoban": "trosoban",
}


def _structure(link: str) -> str:
    for slug, name in _STRUCTURES.items():
        if f"/{slug}" in link:
            return name
    return ""


def _parse(html: str, cfg: Config) -> list[Listing]:
    listings: list[Listing] = []
    for raw in _LDJSON.findall(html):
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get("@type") != "ItemList":
            continue
        for entry in data.get("itemListElement") or []:
            item = entry.get("item") or {}
            link = item.get("url") or ""
            structure = _structure(link)
            if not structure:
                continue
            offer = item.get("offers") or {}
            price = offer.get("price")
            listings.append(
                Listing(
                    site="fourzida",
                    id=link.rstrip("/").rsplit("/", 1)[-1],
                    url=link,
                    price_eur=float(price) if price is not None else None,
                    structure=structure,
                    city=cfg.filters.city,
                    text=f"{cfg.filters.city} {item.get('name', '')} {link}",
                    address=str(item.get("name") or ""),
                )
            )
    return listings


def search(cfg: Config) -> list[Listing]:
    max_rent = int(cfg.filters.max_rent_eur)
    city = fold_city(cfg.filters.city)
    listings: list[Listing] = []
    seen: set[str] = set()
    for structure in cfg.filters.structures:
        slug = _STRUCTURES.get(structure)
        if slug is None:
            continue
        for page in range(1, 16):
            url = (
                f"https://www.4zida.rs/izdavanje-stanova/{city}/{slug}/do-{max_rent}-evra"
                "?sortiranje=najnoviji"
            )
            if page > 1:
                url += f"&strana={page}"
            batch = [item for item in _parse(get_text(url), cfg) if item.id not in seen]
            if not batch:
                break
            seen.update(item.id for item in batch)
            listings.extend(batch)
    return listings


def enrich(listing: Listing) -> Listing:
    html = get_text(listing.url)
    extra: list[str] = []
    for raw in _LDJSON.findall(html):
        data = json.loads(raw)
        if not isinstance(data, dict):
            continue
        block_id = str(data.get("@id") or "")
        if listing.id not in block_id and data.get("@type") not in (
            "Apartment",
            "RealEstateListing",
        ):
            continue
        if data.get("description"):
            extra.append(str(data["description"]))
        for feature in data.get("amenityFeature") or []:
            if isinstance(feature, dict) and feature.get("name"):
                extra.append(str(feature["name"]))
        if data.get("telephone") and listing.id in block_id and not listing.phone:
            listing.phone = re.sub(r"\s+", "", str(data["telephone"]))
    if extra:
        listing.text = listing.text + "\n" + " ".join(extra)
    if not listing.phone:
        soup = BeautifulSoup(html, "html.parser")
        found = _PHONE.search(soup.get_text(" ", strip=True))
        if found:
            listing.phone = re.sub(r"[\s/\-]", "", found.group(0))
    return listing
