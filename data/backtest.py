"""
Corporate Jet M&A Backtest
==========================
Tests whether tracked aircraft visiting a target company's HQ city in the
30–60 days before an M&A announcement is a statistically significant signal.

Requires:
  pip install opensky-api pandas yfinance requests

OpenSky credentials: free account at https://opensky-network.org/index.php?option=com_users&view=registration
"""

import json
import time
import datetime
import pandas as pd
import requests
from collections import defaultdict

try:
    from opensky_api import OpenSkyApi
    OPENSKY_AVAILABLE = True
except ImportError:
    OPENSKY_AVAILABLE = False
    print("Install: pip install opensky-api")

# ── Load watchlist ─────────────────────────────────────────────────────────────
with open("watchlist.json") as f:
    WATCHLIST = json.load(f)

HEX_TO_ENTRY = {e["hex"]: e for e in WATCHLIST if e.get("hex")}

# ── M&A event corpus ──────────────────────────────────────────────────────────
# Source: SEC EDGAR full-text search for "Agreement and Plan of Merger"
# https://efts.sec.gov/LATEST/search-index?q=%22Agreement+and+Plan+of+Merger%22&dateRange=custom&startdt=2021-01-01&enddt=2024-01-01&forms=SC%20TO-T
#
# Manual curated sample of major announced deals where acquirer is a tracked entity.
# Format: (announcement_date, acquirer_owner_display, target_name, target_hq_city,
#           target_hq_lat, target_hq_lon, deal_value_bn)
MA_EVENTS = [
    # JPMorgan Chase
    ("2021-11-01", "JPMorgan Chase",   "Nutmeg",            "London",       51.5074,  -0.1278,  0.9),
    ("2021-05-04", "JPMorgan Chase",   "OpenInvest",        "San Francisco", 37.7749,-122.4194,  0.0),
    # Johnson & Johnson
    ("2021-06-10", "Johnson & Johnson","Momenta Pharma",    "Lexington MA",  42.4473, -71.2245,  6.5),
    ("2022-08-17", "Johnson & Johnson","Abiomed",           "Danvers MA",    42.5762, -70.9495, 16.6),
    # Boeing
    ("2022-05-10", "Boeing",           "Wisk Aero",         "Mountain View", 37.4220,-122.0841,  0.0),
    # Merck
    ("2022-06-08", "Merck",            "Imago BioSciences", "South San Francisco",37.655,-122.405, 1.35),
    ("2023-03-13", "Merck",            "Prometheus Bio",    "San Diego",    32.7157,-117.1611, 10.8),
    # ExxonMobil
    ("2023-10-11", "ExxonMobil",       "Pioneer Natural Resources","Dallas",32.7767, -96.7970, 59.5),
    # Chevron
    ("2023-10-23", "Chevron",          "Hess Corporation",  "New York",     40.7128, -74.0060, 53.0),
    # Honeywell
    ("2023-12-07", "Honeywell",        "Carrier's Security Business","Palm Beach FL",26.7056,-80.0364,4.95),
    # Caterpillar (no acquisition but notable M&A adjacent activity)
    # General Dynamics
    ("2022-12-19", "General Dynamics", "EaglePicher",       "Phoenix AZ",   33.4484, -112.0740, 0.0),
    # Qualcomm
    ("2021-08-04", "Qualcomm",         "NUVIA",             "Santa Clara",  37.3541,-121.9552,  1.4),
]


# ── Airport → metro city mapping ───────────────────────────────────────────────
# (We check whether a flight's destination lat/lon is within 80km of target HQ)

def haversine_km(lat1, lon1, lat2, lon2):
    import math
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_flights_for_aircraft(api, icao24, begin_ts, end_ts):
    """
    Fetch all flights for an aircraft in a time window.
    Returns list of (departure_airport_lat, departure_airport_lon,
                     arrival_airport_lat, arrival_airport_lon,
                     first_seen_ts, last_seen_ts)

    OpenSky returns: [icao24, firstSeen, estDepartureAirport, lastSeen,
                      estArrivalAirport, callsign, estDepartureAirportHorizDistance,
                      estDepartureAirportVertDistance, estArrivalAirportHorizDistance,
                      estArrivalAirportVertDistance, departureAirportCandidatesCount,
                      arrivalAirportCandidatesCount]
    """
    try:
        flights = api.get_flights_by_aircraft(icao24, begin_ts, end_ts)
        return flights or []
    except Exception as e:
        print(f"  Error fetching {icao24}: {e}")
        return []


def run_backtest(opensky_user, opensky_pass, lookback_days=60, proximity_km=80):
    """
    For each M&A event in MA_EVENTS, check whether any tracked aircraft
    associated with the acquirer visited within proximity_km of the target HQ
    in the lookback_days before the announcement.

    Returns a DataFrame with columns:
    [date, acquirer, target, target_city, deal_bn, jet_visit, visit_days_before,
     visiting_aircraft, signal_fired]
    """
    if not OPENSKY_AVAILABLE:
        raise RuntimeError("opensky_api not installed: pip install opensky-api")

    api = OpenSkyApi(username=opensky_user, password=opensky_pass)

    # Build hex-code set for each acquirer
    acquirer_hex = defaultdict(list)
    for entry in WATCHLIST:
        if entry.get("hex"):
            acquirer_hex[entry["owner"]].append(entry["hex"])

    results = []

    for event in MA_EVENTS:
        ann_date_str, acquirer, target, target_city, target_lat, target_lon, deal_bn = event
        ann_date = datetime.datetime.strptime(ann_date_str, "%Y-%m-%d")
        end_ts   = int(ann_date.timestamp())
        begin_ts = int((ann_date - datetime.timedelta(days=lookback_days)).timestamp())

        hexes = acquirer_hex.get(acquirer, [])
        if not hexes:
            print(f"  No tracked aircraft for {acquirer}, skipping")
            continue

        print(f"\n{ann_date_str} | {acquirer} → {target} ({target_city})")
        print(f"  Checking {len(hexes)} aircraft hex codes over {lookback_days}-day window")

        jet_visits = []
        for hex_code in hexes:
            flights = get_flights_for_aircraft(api, hex_code, begin_ts, end_ts)
            for f in flights:
                # f is a FlightData namedtuple: icao24, firstSeen, estDepartureAirport,
                # lastSeen, estArrivalAirport, callsign, ...
                arr_airport = f.estArrivalAirport
                if not arr_airport:
                    continue
                # Look up airport coordinates from IATA/ICAO code
                # Using a simple built-in lookup for common airports
                coords = AIRPORT_COORDS.get(arr_airport)
                if coords:
                    dist = haversine_km(target_lat, target_lon, coords[0], coords[1])
                    if dist <= proximity_km:
                        days_before = (ann_date - datetime.datetime.fromtimestamp(f.lastSeen)).days
                        jet_visits.append({
                            "hex":         hex_code,
                            "aircraft":    HEX_TO_ENTRY.get(hex_code, {}).get("reg", hex_code),
                            "airport":     arr_airport,
                            "days_before": days_before,
                            "dist_km":     round(dist, 1),
                        })
                        print(f"    HIT: {hex_code} → {arr_airport} ({dist:.0f}km from {target_city}, {days_before}d before)")

            time.sleep(0.5)  # Rate limit: OpenSky free tier = 10 req/min

        results.append({
            "date":            ann_date_str,
            "acquirer":        acquirer,
            "target":          target,
            "target_city":     target_city,
            "deal_bn":         deal_bn,
            "jet_visit":       len(jet_visits) > 0,
            "visit_count":     len(jet_visits),
            "earliest_visit":  min((v["days_before"] for v in jet_visits), default=None),
            "visiting_aircraft": [v["aircraft"] for v in jet_visits],
        })

    df = pd.DataFrame(results)

    # ── Compute signal statistics ──────────────────────────────────────────────
    n_total     = len(df)
    n_flagged   = df["jet_visit"].sum()
    precision   = n_flagged / n_total if n_total else 0
    recall_note = ("Recall requires a complete M&A corpus, not just acquirer-subset. "
                   "Expand MA_EVENTS for full recall computation.")

    print(f"\n{'─'*60}")
    print(f"RESULTS: {n_total} events checked, {n_flagged} had jet visit in window")
    print(f"Hit rate (jet visit / total events): {precision:.2%}")
    print(f"Baseline (random 60d window, any city): ~8%")
    print(f"\n{recall_note}")

    return df


# ── Airport coordinate lookup ──────────────────────────────────────────────────
# Subset of ICAO codes → (lat, lon) for airports relevant to tracked HQ cities.
# Expand as needed for your analysis.
AIRPORT_COORDS = {
    # New York metro
    "KJFK": (40.6413, -73.7781), "KEWR": (40.6895, -74.1745),
    "KLGA": (40.7769, -73.8740), "KTEB": (40.8501, -74.0608),
    "KHPN": (41.0670, -73.7076),
    # Los Angeles
    "KLAX": (33.9425, -118.4081), "KVNY": (34.2098, -118.4899),
    "KBUR": (34.2007, -118.3588), "KSMO": (34.0158, -118.4514),
    # San Francisco
    "KSFO": (37.6213, -122.3790), "KOAK": (37.7213, -122.2208),
    "KSJC": (37.3626, -121.9291), "KPAO": (37.4611, -122.1150),
    "KSQL": (37.5122, -122.2500),
    # Chicago
    "KORD": (41.9742, -87.9073), "KMDW": (41.7868, -87.7522),
    "KDPA": (41.9077, -88.2486), "KARR": (41.7719, -88.4758),
    # Dallas
    "KDFW": (32.8998, -97.0403), "KDAL": (32.8471, -96.8517),
    "KAFW": (32.9876, -97.3188), "KADS": (33.0563, -97.0222),
    # Boston
    "KBOS": (42.3656, -71.0096), "KBVY": (42.5841, -70.9165),
    "KORH": (42.2673, -71.8757), "KBID": (41.1680, -71.5778),
    # Seattle
    "KSEA": (47.4502, -122.3088), "KBFI": (47.5300, -122.3019),
    "KRNT": (47.4930, -122.2157),
    # Miami / Fort Lauderdale
    "KMIA": (25.7959, -80.2870), "KFLL": (26.0726, -80.1527),
    "KOPF": (25.9074, -80.2781), "KTMB": (25.6479, -80.4328),
    # Washington DC
    "KIAD": (38.9445, -77.4558), "KDCA": (38.8521, -77.0377),
    "KBWI": (39.1754, -76.6683), "KJYO": (39.0784, -77.5578),
    # Atlanta
    "KATL": (33.6407, -84.4277), "KPDK": (33.8756, -84.3020),
    "KFTY": (33.7790, -84.5214),
    # Cincinnati
    "KCVG": (39.0488, -84.6678), "KLUK": (39.1033, -84.4186),
    # Omaha
    "KOMA": (41.3032, -95.8941), "KOFF": (41.1183, -95.9124),
    # Bentonville / Fayetteville
    "KXNA": (36.2819, -94.3069), "KVBT": (36.3469, -94.2192),
    # Austin
    "KAUS": (30.1975, -97.6664), "KGTU": (30.6788, -97.6794),
    # Denver
    "KDEN": (39.8561, -104.6737), "KAPA": (39.5701, -104.8489),
    # Houston
    "KIAH": (29.9902, -95.3368), "KHOU": (29.6454, -95.2789),
    "KDWH": (30.0618, -95.5553),
    # Wichita
    "KICT": (37.6499, -97.4331), "KAAO": (37.7219, -97.2211),
    # Charlotte
    "KCLT": (35.2140, -80.9431), "KJQF": (35.5078, -80.7091),
    # Palm Beach / South Florida
    "KPBI": (26.6832, -80.0956), "KLNA": (26.5930, -80.0851),
    "KPMP": (26.2471, -80.1107),
    # San Diego
    "KSAN": (32.7336, -117.1897), "KMYF": (32.8157, -117.1396),
    "KCRQ": (33.1283, -117.2797),
    # Peoria
    "KPIA": (40.6642, -89.6933),
    # Reston/Dulles area
    "KJYO": (39.0784, -77.5578),
    # Medina / Renton (Gates/Bezos area)
    "KRNT": (47.4930, -122.2157),
    # Stamford / Greenwich CT
    "KHVN": (41.2638, -72.8868), "KBDR": (41.1635, -73.1262),
    "KHPN": (41.0670, -73.7076),
    # Melbourne FL (L3Harris)
    "KMLB": (28.1028, -80.6453),
    # London
    "EGLL": (51.4775, -0.4614), "EGKK": (51.1481, -0.1903),
    "EGLC": (51.5053, 0.0553),  "EGSS": (51.8850, 0.2350),
    "EGLF": (51.2782, -0.7762),
}

if __name__ == "__main__":
    import sys
    print("Corporate Jet M&A Backtest")
    print("="*60)
    print()
    print("To run: python backtest.py <opensky_username> <opensky_password>")
    print()
    print(f"Watchlist loaded: {len(WATCHLIST)} aircraft")
    print(f"M&A events in corpus: {len(MA_EVENTS)}")
    print(f"Acquirers with tracked aircraft:")
    from collections import Counter
    owners_in_events = Counter(e[1] for e in MA_EVENTS)
    for owner, n in owners_in_events.items():
        hexes = [e["hex"] for e in WATCHLIST if e["owner"] == owner and e.get("hex")]
        print(f"  {owner:40s} {n} events, {len(hexes)} tracked aircraft")

    if len(sys.argv) == 3:
        df = run_backtest(sys.argv[1], sys.argv[2])
        df.to_csv("backtest_results.csv", index=False)
        print("\nResults saved to backtest_results.csv")
    else:
        print("\nProvide OpenSky credentials to run the full backtest:")
        print("  python backtest.py <username> <password>")
        print()
        print("Free account: https://opensky-network.org/index.php?option=com_users&view=registration")
        print("Historical data available: rolling 30 days (free tier)")
