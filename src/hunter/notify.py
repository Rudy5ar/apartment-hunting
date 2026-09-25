import httpx

from hunter.filters import matched_neighborhood
from hunter.listing import Listing


def send(token: str, chat_id: str, text: str) -> None:
    response = httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=20,
    )
    response.raise_for_status()


def format_listing(listing: Listing, neighborhoods: list[str]) -> str:
    area = matched_neighborhood(listing.text + " " + listing.url, neighborhoods) or ""
    lines = [f"{listing.site} · {int(listing.price_eur)} EUR"]
    place = " — ".join(part for part in (area, listing.address) if part)
    if place:
        lines.append(place)
    if listing.phone:
        lines.append(f"tel {listing.phone}")
    lines.append(listing.url)
    return "\n".join(lines)
