import re

from bs4 import BeautifulSoup

from hunter.config import Config
from hunter.http import get_text
from hunter.listing import Listing
from hunter.scrapers.fourzida import fold_city

_ID = re.compile(r"/oglasi/(\d+)/?")
_PRICE = re.compile(r"€\s*([\d.]+)")
_PHONE = re.compile(r"\+381[\d\s/\-]{6,16}|06\d[\d\s/\-]{6,14}")
_SLUGS = {
    "grbavica": "grbavica",
    "liman 3": "liman-iii",
    "liman 4": "liman-iv",
}


def _slug(name: str) -> str:
    key = name.lower().replace("č", "c").replace("ć", "c").strip()
    return _SLUGS.get(key, key.replace(" ", "-"))


def _blocked(html: str) -> bool:
    return "captcha-delivery.com" in html or 'id="cmsg"' in html


def _structure(title: str) -> str:
    low = title.lower()
    if "garsonjer" in low:
        return "garsonjera"
    if "jednosoban" in low:
        return "jednosoban"
    return ""


def _eur(raw: str) -> float:
    return float(raw.replace(".", ""))


def search(cfg: Config) -> list[Listing]:
    city = fold_city(cfg.filters.city)
    listings: list[Listing] = []
    seen: set[str] = set()
    for neighborhood in cfg.filters.neighborhoods:
        slug = _slug(neighborhood)
        url = f"https://www.nekretnine.rs/izdavanje-stanova/{city}/{slug}/"
        html = get_text(url)
        if _blocked(html):
            raise RuntimeError(
                "nekretnine.rs returned a captcha for this IP; other sites keep running"
            )
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.select('a[href*="/oglasi/"]'):
            match = _ID.search(anchor.get("href") or "")
            if not match or match.group(1) in seen:
                continue
            title = (anchor.get("title") or anchor.get_text(" ", strip=True)).strip()
            price_el = anchor.find_previous(class_=re.compile(r"Price_price"))
            price_text = price_el.get_text(" ", strip=True) if price_el else ""
            price_match = _PRICE.search(price_text)
            link = anchor["href"]
            if link.startswith("/"):
                link = "https://www.nekretnine.rs" + link
            seen.add(match.group(1))
            listings.append(
                Listing(
                    site="nekretnine",
                    id=match.group(1),
                    url=link.split("?")[0],
                    price_eur=_eur(price_match.group(1)) if price_match else None,
                    structure=_structure(title),
                    city=cfg.filters.city,
                    text=f"{cfg.filters.city} {title}",
                    address=title[:160],
                )
            )
    return listings


def enrich(listing: Listing) -> Listing:
    html = get_text(listing.url)
    if _blocked(html):
        raise RuntimeError("nekretnine.rs detail page returned a captcha")
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    listing.text += "\n" + text[:12000]
    if not listing.phone:
        found = _PHONE.search(text)
        if found:
            listing.phone = re.sub(r"[\s/\-]", "", found.group(0))
    return listing
