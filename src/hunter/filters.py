import re

from hunter.listing import Listing

_FOLDS = str.maketrans({"č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "dj"})


def fold(value: str) -> str:
    return value.lower().translate(_FOLDS)


def _neighborhood_pattern(name: str) -> re.Pattern[str]:
    key = fold(name).replace("-", " ")
    key = re.sub(r"\s+", " ", key).strip()
    if key in ("liman 3", "liman3"):
        return re.compile(r"liman[\s\-]*iii\b|liman[\s\-]*3(?!\d)")
    if key in ("liman 4", "liman4"):
        return re.compile(r"liman[\s\-]*iv\b|liman[\s\-]*4(?!\d)")
    return re.compile(re.escape(key))


def matched_neighborhood(blob: str, neighborhoods: list[str]) -> str | None:
    folded = fold(blob)
    for name in neighborhoods:
        if _neighborhood_pattern(name).search(folded):
            return name
    return None


def _structure_ok(listing: Listing, structures: list[str]) -> bool:
    got = fold(listing.structure)
    blob = fold(f"{listing.structure} {listing.url} {listing.text}")
    for wanted in structures:
        key = fold(wanted)
        if key == "jednosoban":
            if got == "jednosoban" or "jednosoban" in blob:
                if "garsonjera" in blob and got != "jednosoban" and "jednosoban" not in blob:
                    continue
                return True
            continue
        if key == got or key in blob:
            return True
    return False


def _required_ok(listing: Listing, required: list[str]) -> bool:
    blob = fold(listing.text)
    for term in required:
        key = fold(term)
        if key == "optika":
            if not re.search(r"optik", blob):
                return False
            continue
        if key not in blob:
            return False
    return True


def hard_match(listing: Listing, filters) -> bool:
    blob = fold(f"{listing.city} {listing.text} {listing.url}")
    if fold(filters.city) not in blob:
        return False
    if listing.price_eur is None or listing.price_eur > filters.max_rent_eur:
        return False
    if not _structure_ok(listing, filters.structures):
        return False
    return matched_neighborhood(blob, filters.neighborhoods) is not None


def amenity_match(listing: Listing, filters) -> bool:
    return _required_ok(listing, filters.required)
