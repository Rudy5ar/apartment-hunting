from hunter.scrapers import cityexpert, fourzida, halooglasi, nekretnine

SCRAPERS = {
    "fourzida": fourzida.search,
    "halooglasi": halooglasi.search,
    "nekretnine": nekretnine.search,
    "cityexpert": cityexpert.search,
}

ENRICH = {
    "fourzida": fourzida.enrich,
    "halooglasi": halooglasi.enrich,
    "nekretnine": nekretnine.enrich,
    "cityexpert": cityexpert.enrich,
}
