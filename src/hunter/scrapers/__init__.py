from hunter.scrapers import cityexpert, fourzida, halooglasi

SCRAPERS = {
    "fourzida": fourzida.search,
    "halooglasi": halooglasi.search,
    "cityexpert": cityexpert.search,
}

ENRICH = {
    "fourzida": fourzida.enrich,
    "halooglasi": halooglasi.enrich,
    "cityexpert": cityexpert.enrich,
}
