import argparse
from typing import List

from odoo_jsonrpc import OdooClient, OdooRPCError


def ensure_floor(client: OdooClient, name: str) -> int:
    res = client.search_read("pos.restaurant.floor", [("name", "=", name)], ["id", "name"], limit=1)
    if res:
        return res[0]["id"]
    return client.create("pos.restaurant.floor", {"name": name})


def ensure_table(client: OdooClient, floor_id: int, name: str) -> int:
    res = client.search_read(
        "pos.restaurant.table",
        [("name", "=", name), ("floor_id", "=", floor_id)],
        ["id", "name", "floor_id"],
        limit=1,
    )
    if res:
        return res[0]["id"]
    return client.create("pos.restaurant.table", {"name": name, "seats": 2, "floor_id": floor_id})


def seed_layout(client: OdooClient, floor_name: str, tables: List[str]) -> None:
    floor_id = ensure_floor(client, floor_name)
    created = 0
    for t in tables:
        try:
            ensure_table(client, floor_id, t)
            created += 1
        except OdooRPCError as e:
            print(f"[warn] create table {t} failed: {e}")
    print(f"Seeded floor '{floor_name}' with {created} tables (existing counted as ready).")


def main():
    ap = argparse.ArgumentParser(description="Seed a cafe layout: floor and tables")
    ap.add_argument("--url", default="http://127.0.0.1:18069")
    ap.add_argument("--db", default="wuchang_preview_20251107")
    ap.add_argument("--login", default="admin@wuchang.life")
    ap.add_argument("--password", default="poiuY926")
    ap.add_argument("--floor", default="一樓")
    ap.add_argument("--tables", nargs="*", default=[
        "A1","A2","A3","A4","A5","A6",
        "B1","B2","B3","B4","B5","B6",
    ])
    args = ap.parse_args()

    client = OdooClient(args.url)
    client.authenticate(args.db, args.login, args.password)
    seed_layout(client, args.floor, args.tables)


if __name__ == "__main__":
    main()

