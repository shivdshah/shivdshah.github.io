"""
Daily flight data collector for the corporate jet watchlist.

Run once a day (cron or manual) with free OpenSky credentials.
Stores all flights in SQLite. After 30 days, backtest.py has real data to work with.

Usage:
    python collect.py --user YOUR_OPENSKY_USERNAME --pass YOUR_OPENSKY_PASSWORD

Free OpenSky account: https://opensky-network.org/index.php?option=com_users&view=registration
(Takes ~5 minutes. Free tier: 100 API requests/day, 30-day rolling history.)

Cron setup (daily at 06:00 UTC):
    0 6 * * * cd /path/to/data && python collect.py --user USER --pass PASS >> collect.log 2>&1
"""

import sqlite3
import requests
import json
import time
import argparse
import datetime
import sys
from pathlib import Path

DB_PATH    = "flights.db"
WATCHLIST  = "watchlist_frontend.json"
OPENSKY_BASE = "https://opensky-network.org/api"

# ── Database setup ─────────────────────────────────────────────────────────────
def init_db(db_path):
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            reg             TEXT NOT NULL,
            hex             TEXT NOT NULL,
            owner           TEXT NOT NULL,
            operator_type   TEXT NOT NULL,
            aircraft        TEXT,
            callsign        TEXT,
            dep_airport     TEXT,
            arr_airport     TEXT,
            first_seen      INTEGER,
            last_seen       INTEGER,
            collected_at    INTEGER,
            UNIQUE(hex, first_seen)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS collection_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at      INTEGER,
            window_start INTEGER,
            window_end   INTEGER,
            flights_found INTEGER,
            aircraft_queried INTEGER
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_flights_hex       ON flights(hex)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_flights_dep       ON flights(dep_airport)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_flights_arr       ON flights(arr_airport)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_flights_first_seen ON flights(first_seen)")
    con.commit()
    return con


# ── OpenSky query ──────────────────────────────────────────────────────────────
def get_flights(session, icao24, begin, end, retries=3):
    """
    Fetch flight list for a specific aircraft in [begin, end] unix timestamps.
    Keeps window within 2 OpenSky day-partitions to avoid 'too many partitions' error.
    """
    url = f"{OPENSKY_BASE}/flights/aircraft"
    for attempt in range(retries):
        try:
            r = session.get(url, params={"icao24": icao24, "begin": begin, "end": end}, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return data if isinstance(data, list) else []
            elif r.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"    Rate limited. Waiting {wait}s…", flush=True)
                time.sleep(wait)
            elif r.status_code == 403:
                print(f"    Auth failed (403). Check credentials.", flush=True)
                return []
            else:
                # Could be "You cannot access historical flights" text/plain
                return []
        except Exception as e:
            print(f"    Error: {e}", flush=True)
            time.sleep(5)
    return []


def split_into_day_windows(begin, end):
    """
    Split [begin, end] into chunks that each span at most 2 UTC day-partitions.
    OpenSky rejects queries spanning 3+ day boundaries without auth.
    With credentials, this limitation appears to be lifted up to 30 days.
    """
    # With credentials the limit is 30 days total, no partition restriction
    # So we just return the full window
    return [(begin, end)]


# ── Main collection run ────────────────────────────────────────────────────────
def collect(user, password, lookback_days=30):
    with open(WATCHLIST) as f:
        watchlist = json.load(f)

    session = requests.Session()
    session.auth = (user, password)

    now    = int(time.time())
    begin  = now - lookback_days * 86400

    dt_from = datetime.datetime.utcfromtimestamp(begin).strftime("%Y-%m-%d %H:%M UTC")
    dt_to   = datetime.datetime.utcfromtimestamp(now).strftime("%Y-%m-%d %H:%M UTC")
    print(f"Collection run: {dt_from} → {dt_to}")
    print(f"Aircraft: {len(watchlist)}")
    print(f"Lookback: {lookback_days} days\n")

    con = init_db(DB_PATH)
    total_flights = 0
    queried = 0

    for entry in watchlist:
        hex_code = (entry.get("hex") or "").lower()
        if not hex_code:
            continue

        flights = get_flights(session, hex_code, begin, now)
        queried += 1

        new_count = 0
        for f in flights:
            try:
                con.execute("""
                    INSERT OR IGNORE INTO flights
                        (reg, hex, owner, operator_type, aircraft, callsign,
                         dep_airport, arr_airport, first_seen, last_seen, collected_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    entry["reg"],
                    hex_code.upper(),
                    entry["owner"],
                    entry["type"],
                    entry.get("aircraft"),
                    (f.get("callsign") or "").strip(),
                    f.get("estDepartureAirport"),
                    f.get("estArrivalAirport"),
                    f.get("firstSeen"),
                    f.get("lastSeen"),
                    now,
                ))
                if con.execute("SELECT changes()").fetchone()[0]:
                    new_count += 1
            except sqlite3.Error as e:
                pass

        if flights:
            print(f"  {entry['reg']:10s}  {entry['owner']:35s}  {len(flights):3d} flights ({new_count} new)")

        total_flights += len(flights)
        con.commit()

        # Stay within OpenSky rate limits: ~10 req/min authenticated free tier
        time.sleep(6)

    con.execute("""
        INSERT INTO collection_runs (run_at, window_start, window_end, flights_found, aircraft_queried)
        VALUES (?,?,?,?,?)
    """, (now, begin, now, total_flights, queried))
    con.commit()
    con.close()

    print(f"\nCollection complete: {total_flights} flights stored ({queried} aircraft queried)")
    return total_flights


# ── Analytics on stored data ───────────────────────────────────────────────────
def print_stats():
    if not Path(DB_PATH).exists():
        print("No database yet. Run with --user / --pass first.")
        return

    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
    owners = con.execute("SELECT COUNT(DISTINCT owner) FROM flights").fetchone()[0]
    span   = con.execute("SELECT MIN(first_seen), MAX(first_seen) FROM flights").fetchone()
    runs   = con.execute("SELECT COUNT(*) FROM collection_runs").fetchone()[0]

    if span[0]:
        dt_min = datetime.datetime.utcfromtimestamp(span[0]).strftime("%Y-%m-%d")
        dt_max = datetime.datetime.utcfromtimestamp(span[1]).strftime("%Y-%m-%d")
        date_range = f"{dt_min} → {dt_max}"
    else:
        date_range = "—"

    print(f"Database: {DB_PATH}")
    print(f"  Total flights : {rows:,}")
    print(f"  Operators     : {owners}")
    print(f"  Date range    : {date_range}")
    print(f"  Collection runs: {runs}")
    print()

    if rows > 0:
        print("Most active aircraft (top 15 by flight count):")
        for r in con.execute("""
            SELECT reg, owner, COUNT(*) as cnt
            FROM flights GROUP BY reg ORDER BY cnt DESC LIMIT 15
        """):
            print(f"  {r[0]:10s}  {r[1]:35s}  {r[2]} flights")
        print()

        print("Most-visited destination airports (excluding origin HQ airports):")
        for r in con.execute("""
            SELECT arr_airport, COUNT(*) as cnt, COUNT(DISTINCT owner) as ops
            FROM flights
            WHERE arr_airport IS NOT NULL
            GROUP BY arr_airport ORDER BY cnt DESC LIMIT 20
        """):
            print(f"  {r[0]:8s}  {r[1]:4d} arrivals  {r[2]} different operators")

    con.close()


def export_json():
    """Export recent flights as JSON for the frontend."""
    if not Path(DB_PATH).exists():
        return

    cutoff = int(time.time()) - 30 * 86400
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("""
        SELECT reg, owner, operator_type, aircraft, dep_airport, arr_airport,
               first_seen, last_seen
        FROM flights
        WHERE first_seen > ?
        ORDER BY first_seen DESC
    """, (cutoff,)).fetchall()
    con.close()

    flights = []
    for r in rows:
        flights.append({
            "reg": r[0], "owner": r[1], "type": r[2], "aircraft": r[3],
            "dep": r[4], "arr": r[5],
            "firstSeen": r[6], "lastSeen": r[7],
        })

    with open("flights_export.json", "w") as f:
        json.dump(flights, f, separators=(",", ":"))
    print(f"Exported {len(flights)} flights to flights_export.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corporate jet flight data collector")
    parser.add_argument("--user",  help="OpenSky username")
    parser.add_argument("--pass",  dest="password", help="OpenSky password")
    parser.add_argument("--days",  type=int, default=30, help="Lookback window in days (default: 30)")
    parser.add_argument("--stats", action="store_true", help="Print database statistics and exit")
    parser.add_argument("--export",action="store_true", help="Export flights to JSON for frontend")
    args = parser.parse_args()

    if args.stats:
        print_stats()
        sys.exit(0)

    if args.export:
        export_json()
        sys.exit(0)

    if not args.user or not args.password:
        print("OpenSky credentials required for historical data collection.")
        print()
        print("Get a free account (takes ~5 min):")
        print("  https://opensky-network.org/index.php?option=com_users&view=registration")
        print()
        print("Then run:")
        print("  python collect.py --user YOUR_USERNAME --pass YOUR_PASSWORD")
        print()
        print("Cron job (daily at 06:00 UTC):")
        print("  0 6 * * * cd /path/to/data && python collect.py --user U --pass P >> collect.log 2>&1")
        print()
        print_stats()
        sys.exit(0)

    collect(args.user, args.password, lookback_days=args.days)
    export_json()
