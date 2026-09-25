from dataclasses import dataclass


@dataclass
class Listing:
    site: str
    id: str
    url: str
    price_eur: float | None
    structure: str
    city: str
    text: str
    address: str = ""
    phone: str = ""
