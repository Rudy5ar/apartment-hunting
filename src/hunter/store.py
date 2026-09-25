import sqlite3
from pathlib import Path


class Store:
    def __init__(self, path: str = "data/seen.db") -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute(
            "create table if not exists seen (site text, id text, primary key (site, id))"
        )
        self.db.execute("create table if not exists ready (site text primary key)")
        self.db.commit()

    def seen(self, site: str, listing_id: str) -> bool:
        row = self.db.execute(
            "select 1 from seen where site = ? and id = ?", (site, listing_id)
        ).fetchone()
        return row is not None

    def mark(self, site: str, listing_id: str) -> None:
        self.db.execute(
            "insert or ignore into seen (site, id) values (?, ?)", (site, listing_id)
        )
        self.db.commit()

    def is_ready(self, site: str) -> bool:
        row = self.db.execute("select 1 from ready where site = ?", (site,)).fetchone()
        return row is not None

    def set_ready(self, site: str) -> None:
        self.db.execute("insert or ignore into ready (site) values (?)", (site,))
        self.db.commit()
