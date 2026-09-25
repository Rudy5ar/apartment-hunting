import os
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Filters:
    city: str
    structures: list[str]
    max_rent_eur: float
    neighborhoods: list[str]
    required: list[str]


@dataclass
class Site:
    id: str
    enabled: bool


@dataclass
class Config:
    poll_seconds: int
    filters: Filters
    sites: list[Site]


def load_env(path: str = ".env") -> None:
    file = Path(path)
    if not file.exists():
        return
    for line in file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config(path: str | None = None) -> Config:
    file = Path(path or os.environ.get("HUNTER_CONFIG", "config.yaml"))
    raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    filters = raw["filters"]
    return Config(
        poll_seconds=int(raw.get("poll_seconds", 45)),
        filters=Filters(
            city=str(filters["city"]),
            structures=[str(item) for item in filters["structures"]],
            max_rent_eur=float(filters["max_rent_eur"]),
            neighborhoods=[str(item) for item in filters["neighborhoods"]],
            required=[str(item) for item in filters.get("required", [])],
        ),
        sites=[
            Site(id=str(item["id"]), enabled=bool(item.get("enabled", True)))
            for item in raw["sites"]
        ],
    )
