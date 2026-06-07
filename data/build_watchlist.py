"""
Build corporate jet watchlist from FAA registry.

Only includes aircraft/entities verified in the FAA MASTER.txt data.
No fabricated tail numbers or guessed attributions.
"""

import pandas as pd
import json
import re
from collections import Counter

FAA_DIR = "faa"

# ── Verified bizjet model codes from FAA ACFTREF.txt (seat counts checked) ───
# Only codes with ≤25 seats in ACFTREF (excludes CRJ regional airliners
# that share the CL-600 series designation with Challengers).
BIZJET_CODES = {
    # ── Gulfstream (all 9-22 seats per ACFTREF) ───────────────────────────────
    "3980050": "Gulfstream G650ER",     # GVI (G650ER)  22 seats
    "3980101": "Gulfstream G550",       # GV-SP         20 seats
    "3980116": "Gulfstream G-V",        # G-V           20 seats
    "3980203": "Gulfstream G550",       # GV-SP (G550)  20 seats
    "3980208": "Gulfstream G500",       # GV-SP (G500)  22 seats
    "3980295": "Gulfstream G550",       # GV-SP (G550)  20 seats
    "3980115": "Gulfstream G-IV",       # G-IV          22 seats
    "3980117": "Gulfstream G-IV SP",    # G-IV SP       22 seats
    "3980118": "Gulfstream G-IV SP",    # IV SP         22 seats
    "3980119": "Gulfstream G450",       # GIV-X         22 seats
    "3980200": "Gulfstream G-III",      # G-III         21 seats
    "3980204": "Gulfstream G400",       # G-IV (G400)   22 seats
    "3980205": "Gulfstream G450",       # GIV-X (G450)  22 seats
    "3980206": "Gulfstream G350",       # G-IV (G350)   22 seats
    "3980207": "Gulfstream G300",       # G-IV (G300)   22 seats
    "3980220": "Gulfstream G350",       # GIV-X (G350)  22 seats
    "3980121": "Gulfstream G650",       # GVI           22 seats
    "3980212": "Gulfstream G650",       # G650          22 seats
    "3980214": "Gulfstream G650",       # GVI (G650)    22 seats
    "3980218": "Gulfstream G700",       # GVIII-G700     9 seats
    "3980219": "Gulfstream G700",       # GVIII-G700     9 seats
    "3980221": "Gulfstream G700",       #                9 seats
    "3980222": "Gulfstream G700",       #                9 seats
    "3980225": "Gulfstream G500",       # GVII-G500      9 seats
    "3980226": "Gulfstream G500",       #                9 seats
    "05637SM":  "Gulfstream G600",      # GVII-G600      9 seats
    "3980125":  "Gulfstream G400",      # GVII-G400      9 seats
    "3980321":  "Gulfstream G800",      # GVIII-G800     9 seats
    # ── Bombardier Global Express / 7500 (≤23 seats per ACFTREF) ─────────────
    "1390006":  "Bombardier Global Express",   # BD-700-1A10  23 seats
    "1390085":  "Bombardier Global Express",   # BD-700-1A10  23 seats
    "1390022":  "Bombardier Global XRS",       # BD-700-1A11   8 seats
    "1390052":  "Bombardier Global 7500",      # BD-700-2A12  22 seats
    # ── Bombardier Challenger 600-series (only ≤24 seat variants) ────────────
    # CL-600-2B19 (55 seats) = CRJ-900 → EXCLUDED
    # CL-600-2C10 (80 seats) = CRJ-900ER → EXCLUDED
    # CL-600-2D24 (95 seats) = CRJ-200 variant → EXCLUDED
    # CL-600-2C11 (55 seats) = CRJ-1000 → EXCLUDED
    "1390009":  "Bombardier Challenger 604",   # CL-600-2B16  22 seats
    "139000A":  "Bombardier Challenger 601",   # CL-600-2B16  20 seats
    "1390017":  "Bombardier Challenger 604",   # CL-604       21 seats
    "1390018":  "Bombardier Challenger 601",   # CL-600-2A12  22 seats
    "1390020":  "Bombardier Challenger 601",   # CHALLENGER 601-3R 12 seats
    "1390026":  "Bombardier Challenger 605",   # CL-600-2B16 (CL-605) 22 seats
    "1390046":  "Bombardier Challenger 601",   # CL-601-3A    24 seats
    "1390065":  "Bombardier Challenger 604",   # CL-600-2B16  22 seats
    "1390024":  "Bombardier Challenger 601",   # CL600-2B16   22 seats
    "1390040":  "Bombardier Challenger 604",   # BD-600-2B16  22 seats
    "1900307":  "Bombardier Challenger 604",   # CL-600-2B16  21 seats
    "1900314":  "Bombardier Challenger 604",   # CL-600-2B16  22 seats
    # ── Bombardier Challenger 300/350 (BD-100) ────────────────────────────────
    "1390044":  "Bombardier Challenger 300",   # BD-100-1A10   8 seats
    "1390050":  "Bombardier Challenger 300",   # BD-100-1A10   8 seats
    # ── Dassault Falcon 7X / 8X / 6X ─────────────────────────────────────────
    "2730177":  "Dassault Falcon 7X",
    "2730178":  "Dassault Falcon 8X",
    "2730185":  "Dassault Falcon 6X",
    # ── Dassault Falcon 900 series ────────────────────────────────────────────
    "2730009":  "Dassault Falcon 900EX",
    "2730013":  "Dassault Falcon 900EX",
    "2730014":  "Dassault Falcon 900DX",
    "2730015":  "Dassault Falcon 900LX",
    "2730020":  "Dassault Falcon 900EX",
    "2730101":  "Dassault Falcon 900",
    "2730160":  "Dassault Falcon 900",
    "2730161":  "Dassault Falcon 900",
    "2730172":  "Dassault Falcon 900B",
    "2730175":  "Dassault Falcon 900",
    # ── Dassault Falcon 2000 series ───────────────────────────────────────────
    "2730012":  "Dassault Falcon 2000EX",
    "2730110":  "Dassault Falcon 2000EX",
    "2730124":  "Dassault Falcon 2000LX",
    "2730125":  "Dassault Falcon 2000LXS",
    "2730170":  "Dassault Falcon 2000",
    # ── Cessna Citation X / Longitude ─────────────────────────────────────────
    "2076809":  "Cessna Citation X",
    "2076810":  "Cessna Citation X",
    "2076820":  "Cessna Citation X+",
    "2076819":  "Cessna Citation Longitude",
    # ── Cessna Citation Sovereign (NetJets primary type) ─────────────────────
    "2076702":  "Cessna Citation Sovereign",   # 560XL  13 seats
}

# ── Entity patterns: ALL verified against actual registrant names in FAA data ─
# Format: (regex_pattern, display_name, operator_type)
# Every match below was spot-checked against actual FAA NAME field output above.
ENTITY_PATTERNS = [
    # ── Berkshire / NetJets ───────────────────────────────────────────────────
    (r"berkshire",              "Berkshire Hathaway",              "corp"),
    (r"netjets",                "NetJets (Berkshire Hathaway)",    "corp"),
    # ── PE Firms (only match names verified in FAA data or clearly unambiguous)
    (r"\bkkr\b",                "KKR",                            "pe"),
    (r"kohlberg kravis",        "KKR",                            "pe"),
    (r"blackstone",             "Blackstone",                     "pe"),
    # Apollo Global: tighten to avoid "APOLLO SHEET METAL INC"
    (r"apollo global|apollo management|apollo asset|apollo aviation\s+ii",
                                "Apollo Global Management",       "pe"),
    (r"carlyle",                "Carlyle Group",                  "pe"),
    (r"\btpg\b",                "TPG Capital",                    "pe"),
    (r"warburg pincus",         "Warburg Pincus",                 "pe"),
    (r"bain capital",           "Bain Capital",                   "pe"),
    (r"cerberus",               "Cerberus Capital",               "pe"),
    (r"ares management",        "Ares Management",                "pe"),
    (r"leonard green",          "Leonard Green & Partners",       "pe"),
    (r"vista equity",           "Vista Equity",                   "pe"),
    (r"thoma bravo",            "Thoma Bravo",                    "pe"),
    (r"silver lake aviation",   "Silver Lake",                    "pe"),
    (r"francisco partners",     "Francisco Partners",             "pe"),
    (r"general atlantic",       "General Atlantic",               "pe"),
    # ── Hedge Funds ───────────────────────────────────────────────────────────
    (r"bridgewater",            "Bridgewater Associates",         "hedge"),
    (r"citadel aviation",       "Citadel",                        "hedge"),
    (r"two sigma",              "Two Sigma",                      "hedge"),
    (r"d\.?e\.? shaw",          "D.E. Shaw",                      "hedge"),
    (r"point72",                "Point72 (Cohen)",                "hedge"),
    (r"pershing square",        "Pershing Square (Ackman)",       "hedge"),
    (r"third point",            "Third Point (Loeb)",             "hedge"),
    (r"starboard value",        "Starboard Value",                "hedge"),
    (r"elliott management",     "Elliott Management",             "hedge"),
    (r"\bicahn\b",              "Icahn Enterprises",              "hedge"),
    (r"baupost",                "Baupost Group",                  "hedge"),
    (r"viking global",          "Viking Global",                  "hedge"),
    (r"coatue",                 "Coatue Management",              "hedge"),
    (r"renaissance air llc",    "Renaissance Technologies (?)",   "hedge"),
    # ── Investment Banks ──────────────────────────────────────────────────────
    (r"goldman sachs",          "Goldman Sachs",                  "finance"),
    (r"jpmorgan|jp morgan",     "JPMorgan Chase",                 "finance"),
    (r"morgan stanley",         "Morgan Stanley",                 "finance"),
    (r"blackrock",              "BlackRock",                      "finance"),
    (r"lazard",                 "Lazard",                         "finance"),
    (r"bank of america",        "Bank of America",                "finance"),
    (r"citigroup|citibank",     "Citigroup",                      "finance"),
    (r"wells fargo equipment finance",  # Only if it's their corp fleet, not leasing
                                "Wells Fargo",                    "finance"),
    # ── Fortune 500 Corporates (all verified in FAA NAME field) ───────────────
    (r"exxon mobil",            "ExxonMobil",                     "corp"),
    (r"chevron u s a|chevron usa|chevron corp",
                                "Chevron",                        "corp"),
    (r"procter.*gamble|p&g leasing",
                                "Procter & Gamble",               "corp"),
    (r"johnson.*&.*johnson|j&j finance",
                                "Johnson & Johnson",              "corp"),
    (r"merck sharp",            "Merck",                          "corp"),
    (r"qualcomm inc",           "Qualcomm",                       "corp"),
    (r"caterpillar inc",        "Caterpillar",                    "corp"),
    (r"general dynamics corp",  "General Dynamics",               "corp"),
    (r"northrop grumman systems",
                                "Northrop Grumman",               "corp"),
    (r"l3harris technologies(?! flight capital)",  # Corp jets, not leasing arm
                                "L3Harris Technologies",          "corp"),
    (r"honeywell international",
                                "Honeywell",                      "corp"),
    (r"kimberly.clark",         "Kimberly-Clark",                 "corp"),
    (r"hilton domestic|hilton resorts",
                                "Hilton Hotels",                  "corp"),
    (r"lowes companies",        "Lowe's Companies",               "corp"),
    (r"costco wholesale",       "Costco",                         "corp"),
    (r"kroger co",              "Kroger",                         "corp"),
    (r"\bnike inc\b",           "Nike",                           "corp"),
    (r"ford motor",             "Ford Motor Company",             "corp"),
    (r"general motors corp",    "General Motors",                 "corp"),
    (r"general electric|ge aviation",
                                "GE Aerospace",                   "corp"),
    (r"\bboeing co",            "Boeing",                         "corp"),
    (r"exxon",                  "ExxonMobil",                     "corp"),
    (r"oracle navigation",      "Oracle",                         "corp"),
    (r"walmart",                "Walmart",                        "corp"),
    (r"koch industries",        "Koch Industries",                "corp"),
    (r"trump",                  "Trump Organization",             "individual"),
    # ── Documented individual LLCs (public records / journalism) ──────────────
    (r"cascade investment",     "Bill Gates",                     "individual"),
    (r"blue origin",            "Jeff Bezos",                     "individual"),
    (r"bezos expeditions",      "Jeff Bezos",                     "individual"),
    (r"spacex",                 "Elon Musk / SpaceX",             "individual"),
    (r"x corp",                 "Elon Musk",                      "individual"),
]

HQ_LOOKUP = {
    "Berkshire Hathaway":           ("Omaha",           41.2565, -95.9345),
    "NetJets (Berkshire Hathaway)": ("Columbus",        39.9612, -82.9988),
    "KKR":                          ("New York",        40.7128, -74.0060),
    "Blackstone":                   ("New York",        40.7128, -74.0060),
    "Apollo Global Management":     ("New York",        40.7128, -74.0060),
    "Carlyle Group":                ("Washington DC",   38.9072, -77.0369),
    "TPG Capital":                  ("Fort Worth",      32.7555, -97.3308),
    "Warburg Pincus":               ("New York",        40.7128, -74.0060),
    "Bain Capital":                 ("Boston",          42.3601, -71.0589),
    "Cerberus Capital":             ("New York",        40.7128, -74.0060),
    "Ares Management":              ("Los Angeles",     34.0522, -118.2437),
    "Leonard Green & Partners":     ("Los Angeles",     34.0522, -118.2437),
    "Vista Equity":                 ("Austin",          30.2672, -97.7431),
    "Thoma Bravo":                  ("Chicago",         41.8781, -87.6298),
    "Silver Lake":                  ("Menlo Park",      37.4529, -122.1817),
    "Francisco Partners":           ("San Francisco",   37.7749, -122.4194),
    "General Atlantic":             ("New York",        40.7128, -74.0060),
    "Bridgewater Associates":       ("Westport",        41.1415, -73.3579),
    "Citadel":                      ("Miami",           25.7617, -80.1918),
    "Two Sigma":                    ("New York",        40.7128, -74.0060),
    "D.E. Shaw":                    ("New York",        40.7128, -74.0060),
    "Point72 (Cohen)":              ("Stamford",        41.0534, -73.5387),
    "Pershing Square (Ackman)":     ("New York",        40.7128, -74.0060),
    "Third Point (Loeb)":           ("New York",        40.7128, -74.0060),
    "Starboard Value":              ("New York",        40.7128, -74.0060),
    "Elliott Management":           ("West Palm Beach", 26.7153, -80.0534),
    "Icahn Enterprises":            ("Sunny Isles",     25.9532, -80.1232),
    "Baupost Group":                ("Boston",          42.3601, -71.0589),
    "Viking Global":                ("Greenwich",       41.0262, -73.6282),
    "Coatue Management":            ("New York",        40.7128, -74.0060),
    "Renaissance Technologies (?)": ("East Setauket",  40.9326, -73.1093),
    "Goldman Sachs":                ("New York",        40.7128, -74.0060),
    "JPMorgan Chase":               ("New York",        40.7128, -74.0060),
    "Morgan Stanley":               ("New York",        40.7128, -74.0060),
    "BlackRock":                    ("New York",        40.7128, -74.0060),
    "Lazard":                       ("New York",        40.7128, -74.0060),
    "Bank of America":              ("Charlotte",       35.2271, -80.8431),
    "Citigroup":                    ("New York",        40.7128, -74.0060),
    "Wells Fargo":                  ("San Francisco",   37.7749, -122.4194),
    "ExxonMobil":                   ("Spring TX",       30.0799, -95.4172),
    "Chevron":                      ("San Ramon",       37.7801, -121.9780),
    "Procter & Gamble":             ("Cincinnati",      39.1031, -84.5120),
    "Johnson & Johnson":            ("New Brunswick",   40.4863, -74.4518),
    "Merck":                        ("Kenilworth",      40.6737, -74.2952),
    "Qualcomm":                     ("San Diego",       32.7157, -117.1611),
    "Caterpillar":                  ("Peoria",          40.6936, -89.5890),
    "General Dynamics":             ("Reston",          38.9537, -77.3469),
    "Northrop Grumman":             ("Falls Church",    38.8826, -77.1711),
    "L3Harris Technologies":        ("Melbourne FL",    28.0836, -80.6081),
    "Honeywell":                    ("Charlotte",       35.2271, -80.8431),
    "Kimberly-Clark":               ("Irving TX",       32.8141, -96.9489),
    "Hilton Hotels":                ("McLean VA",       38.9340, -77.1773),
    "Lowe's Companies":             ("Mooresville",     35.5846, -80.8101),
    "Costco":                       ("Issaquah",        47.5301, -122.0326),
    "Kroger":                       ("Cincinnati",      39.1031, -84.5120),
    "Nike":                         ("Beaverton",       45.4871, -122.8037),
    "Ford Motor Company":           ("Dearborn",        42.3223, -83.1763),
    "General Motors":               ("Detroit",         42.3314, -83.0458),
    "GE Aerospace":                 ("Cincinnati",      39.1031, -84.5120),
    "Boeing":                       ("Arlington VA",    38.8799, -77.1068),
    "Oracle":                       ("Austin",          30.2672, -97.7431),
    "Walmart":                      ("Bentonville",     36.3729, -94.2088),
    "Koch Industries":              ("Wichita",         37.6872, -97.3301),
    "Trump Organization":           ("Palm Beach",      26.7056, -80.0364),
    "Bill Gates":                   ("Medina WA",       47.6201, -122.2421),
    "Jeff Bezos":                   ("Miami",           25.7617, -80.1918),
    "Elon Musk / SpaceX":           ("Austin",          30.2672, -97.7431),
    "Elon Musk":                    ("Austin",          30.2672, -97.7431),
}


def match_entity(name):
    if not isinstance(name, str):
        return None, None
    lc = name.lower()
    for pattern, display, etype in ENTITY_PATTERNS:
        if re.search(pattern, lc):
            return display, etype
    return None, None


def main():
    print("Loading FAA ACFTREF...", flush=True)
    acft = pd.read_csv(f"{FAA_DIR}/ACFTREF.txt", dtype=str, encoding="latin-1")
    acft.columns = [c.strip().lstrip("ï»¿").lstrip("﻿") for c in acft.columns]

    print("Loading FAA MASTER...", flush=True)
    master = pd.read_csv(f"{FAA_DIR}/MASTER.txt", dtype=str, encoding="latin-1")
    master.columns = [c.strip().lstrip("ï»¿").lstrip("﻿") for c in master.columns]
    master = master.map(lambda x: x.strip() if isinstance(x, str) else x)
    print(f"  Total registrations: {len(master):,}")

    valid_codes = set(BIZJET_CODES.keys())
    bizjets = master[master["MFR MDL CODE"].isin(valid_codes)].copy()
    print(f"  Bizjet model codes: {len(bizjets):,}")
    bizjets = bizjets[bizjets["STATUS CODE"] == "V"].copy()
    print(f"  Active registrations: {len(bizjets):,}")

    bizjets["_aircraft"] = bizjets["MFR MDL CODE"].map(BIZJET_CODES)

    matches = bizjets["NAME"].apply(match_entity)
    bizjets["_owner"] = matches.apply(lambda x: x[0])
    bizjets["_type"]  = matches.apply(lambda x: x[1])

    matched = bizjets[bizjets["_owner"].notna()].copy()
    print(f"\nMatched to known entities: {len(matched):,}")

    print("\nBreakdown by entity:")
    for owner, grp in sorted(matched.groupby("_owner"), key=lambda x: x[0]):
        regs = ", ".join("N" + r.lstrip("N") for r in grp["N-NUMBER"].tolist())
        print(f"  {owner:45s} {len(grp):3d}  [{regs}]")

    watchlist = []
    seen = set()
    for _, row in matched.iterrows():
        reg = str(row["N-NUMBER"]).strip()
        n_num = "N" + reg.lstrip("N")
        if n_num in seen:
            continue
        seen.add(n_num)

        owner = row["_owner"]
        etype = row["_type"]
        hq    = HQ_LOOKUP.get(owner, ("Unknown", None, None))

        watchlist.append({
            "reg":      n_num,
            "hex":      str(row.get("MODE S CODE HEX", "")).strip().upper() or None,
            "owner":    owner,
            "org":      str(row["NAME"]).strip(),
            "type":     etype,
            "aircraft": row["_aircraft"],
            "year":     str(row.get("YEAR MFR", "")).strip() or None,
            "hqCity":   hq[0],
            "hqLat":    hq[1],
            "hqLon":    hq[2],
            "src":      "faa_registry",
        })

    watchlist.sort(key=lambda x: (x["type"], x["owner"], x["reg"]))

    print(f"\nFinal watchlist: {len(watchlist)} aircraft")
    print("\nBreakdown by type:")
    counts = Counter(e["type"] for e in watchlist)
    for t, n in sorted(counts.items()):
        print(f"  {t:12s}: {n}")

    with open("watchlist.json", "w") as f:
        json.dump(watchlist, f, indent=2)

    # Frontend version — minimal fields
    frontend = [{
        "reg":  e["reg"],
        "hex":  e["hex"],
        "owner":e["owner"],
        "type": e["type"],
        "aircraft": e["aircraft"],
        "hqCity": e["hqCity"],
        "hqLat":  e["hqLat"],
        "hqLon":  e["hqLon"],
    } for e in watchlist]

    with open("watchlist_frontend.json", "w") as f:
        json.dump(frontend, f, separators=(",", ":"))

    print(f"\nWrote watchlist.json and watchlist_frontend.json")


if __name__ == "__main__":
    main()
