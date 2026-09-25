import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hunter.config import Filters
from hunter.filters import amenity_match, hard_match
from hunter.listing import Listing

FILTERS = Filters(
    city="novi sad",
    structures=["jednosoban"],
    max_rent_eur=350,
    neighborhoods=["grbavica", "liman 3", "liman 4"],
    required=["klima", "optika"],
)


def listing(**overrides) -> Listing:
    data = dict(
        site="fourzida",
        id="1",
        url="https://www.4zida.rs/izdavanje-stanova/liman-3-novi-sad/jednosoban-stan/abc",
        price_eur=300,
        structure="jednosoban",
        city="novi sad",
        text="novi sad Liman 3 jednosoban klima optika",
        address="Bulevar",
    )
    data.update(overrides)
    return Listing(**data)


def main() -> None:
    assert hard_match(listing(), FILTERS)
    assert amenity_match(listing(), FILTERS)
    assert hard_match(
        listing(
            text="novi sad liman-iii jednosoban klima optički",
            url="https://x/jednosoban-stan/abc",
        ),
        FILTERS,
    )
    assert not hard_match(
        listing(
            text="novi sad Liman 1 jednosoban klima optika",
            url="https://x/liman-1/jednosoban-stan/abc",
        ),
        FILTERS,
    )
    assert not hard_match(
        listing(
            text="novi sad Liman 2 jednosoban klima optika",
            url="https://x/liman-2/jednosoban-stan/abc",
        ),
        FILTERS,
    )
    assert not hard_match(listing(price_eur=351), FILTERS)
    assert not hard_match(listing(structure="garsonjera", text="novi sad Liman 3 garsonjera klima optika", url="https://x/garsonjera"), FILTERS)
    assert not amenity_match(listing(text="novi sad Liman 3 jednosoban optika"), FILTERS)
    assert not amenity_match(listing(text="novi sad Liman 3 jednosoban klima"), FILTERS)
    print("ok")


if __name__ == "__main__":
    main()
