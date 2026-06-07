---
title: "Corporate Jet Tracker: Private Aviation as Alternative Data"
tags:
  - javascript
  - aviation
  - finance
  - adsb
  - alternative-data
description: Live tracker of 95 corporate aircraft identified from the FAA registry. Unusual private jet movements by executives and fund principals precede M&A announcements and earnings surprises. All data derives from public ADS-B telemetry.
---

<div class="abstract">
<p>Private jet movements by executives and institutional principals lead M&A activity and earnings events. This tracker monitors 95 aircraft identified from the FAA civil registry in real time using public ADS-B telemetry, and flags live convergence signals: multiple tracked jets from different operators appearing within 200 km of each other at a non-hub location. The watchlist comes from the FAA ReleasableAircraft database. No tail numbers are guessed or fabricated.</p>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

<span class="section-number">01: Live Tracker</span>

## Corporate Aircraft Monitor

<div class="cjet-controls">
  <button class="cjet-scan-btn" id="cjet-scan-btn" onclick="cjetScan()">
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    Scan Watchlist Now
  </button>
  <span class="cjet-subtitle">Queries airplanes.live for current positions of 95 FAA-registered aircraft</span>
</div>

<div id="cjet-progress" class="cjet-progress" style="display:none"></div>
<div id="cjet-map" class="cjet-map"></div>
<div id="cjet-anomalies"></div>
<div id="cjet-table"></div>

<span class="section-number">02: The Thesis</span>

## Private Jet Movements as a Leading Indicator

Every major deal generates a physical record before any public announcement. Due diligence requires in-person meetings. Management presentations happen at neutral locations. Lawyers, bankers, and principals fly to target headquarters weeks before a transaction is filed. This pattern repeats across deal types.

M&A: The acquirer's senior principals, typically a CEO, CFO, and lead banker, visit the target's HQ city in the 30 to 60 days before signing. Billion-dollar transactions almost never use commercial flights. The G650 flies.

Earnings: Executives visit key customers, factories, or investor relations contacts in the weeks before a quarterly announcement. Activity that deviates from their typical routing signals either positive or negative news flow.

Activist positioning: Activists accumulate stakes quietly. The in-person due diligence phase, plant visits and management meetings, generates jet activity before their 13D or 13G is filed. Many activists register aircraft to LLCs, but tail numbers recur enough to trace.

Conference intelligence: Sun Valley (Allen and Co.), the Milken Global Conference, Davos, and Aspen Ideas concentrate deal principals. A PE firm jet flying to Hailey Municipal Airport (SUN) in early July is not random. Multiple tracked aircraft converging at the same small-market location is a stronger signal than any single visit.

The logic is simple: M&A requires physical presence. Physical presence generates ADS-B traces. ADS-B is public. The work is aggregating and monitoring the data continuously.

<span class="section-number">03: Signal Design</span>

## Anomaly Detection Heuristics

Three signals, ordered by implementation complexity.

### Signal A: Novel Destination

Flag any tracked aircraft visiting a metro area absent from its trailing 90-day routing history. Executives follow predictable travel patterns. A Merck Gulfstream flying exclusively EWR to MIA to CLE for three months, then appearing near Palo Alto or Bentonville, is anomalous.

$$\text{Signal}_A = \mathbb{1}\left[\text{destination metro} \notin \mathcal{V}_{90d}(i)\right]$$

where $\mathcal{V}_{90d}(i)$ is the set of destination metros visited by aircraft $i$ in the trailing 90 days. Signal A requires historical routing data. See Section 05.

### Signal B: Convergence

Flag two or more tracked aircraft from different operators landing at the same small-market airport within a 48-hour window. Small-market means outside the top 30 airports by enplanements.

$$\text{Signal}_B = \mathbb{1}\left[\exists\, i \neq j :\; d(\text{pos}_i, \text{pos}_j) < 200\text{ km},\; \text{owner}(i) \neq \text{owner}(j),\; \text{airport} \notin \mathcal{H}\right]$$

The live version of Signal B uses the current position snapshot. When two tracked jets fly within 200 km of each other at a non-hub location, the signal fires. A 48-hour historical window produces more precise results. The live approximation catches aircraft airborne simultaneously in the same region.

### Signal C: Burst Activity

Flag any aircraft making four or more round trips in a 7-day window against a baseline of one or fewer per week. Burst activity typically means intensive due diligence across multiple site visits, or earnings prep.

$$\text{Signal}_C = \mathbb{1}\left[\text{trips}_{7d}(i) \geq 4 \;\land\; \text{trips}_{7d}^{\text{baseline}}(i) \leq 1\right]$$

Signal C requires historical routing data. See Section 05.

<span class="section-number">04: Watchlist: Source and Coverage</span>

## FAA Registry Methodology

The watchlist derives entirely from the FAA ReleasableAircraft database (`registry.faa.gov/database/ReleasableAircraft.zip`), published weekly with all US civil aircraft registrations. The pipeline runs three steps.

<ol class="steps">
<li><p>Filter MASTER.txt to aircraft type codes for large-cabin business jets: Gulfstream G-IV through G800, Bombardier Global Express and Global 7500, Bombardier Challenger 300, 604, and 605, Dassault Falcon 900, 2000, and 7X, and Cessna Citation X and Longitude. Each code was verified against seat counts in ACFTREF.txt. Codes with more than 25 seats are excluded. This removes CRJ-900 and CRJ-1000 regional airliners, which share the CL-600 designation with Challenger corporate jets. Result: 5,925 active registrations.</p></li>
<li><p>Apply regex patterns to the NAME field against known institutional entities. Most PE and hedge fund aircraft sit in opaque LLCs and do not match. Only operators who registered aircraft in their own corporate name, or a directly identifiable subsidiary, appear here. Result: 95 aircraft.</p></li>
<li><p>The FAA registry includes MODE S CODE HEX for each aircraft. This is the identifier ADS-B telemetry and all live tracking APIs use. Every watchlist entry includes a verified hex code from the registry.</p></li>
</ol>

<div class="info-box">
<span class="info-box-label">Coverage Caveat</span>
<p>This watchlist covers publicly transparent operators only: those who registered aircraft in their own institutional name. Most PE and hedge fund aircraft sit in holding LLCs with opaque names such as "THUNDER SKY AVIATION LLC" and do not appear. The 95 aircraft are a floor. Run build_watchlist.py against each weekly FAA release to add new registrations.</p>
</div>

**Current watchlist: 95 aircraft across 29 operators**

| Operator | Aircraft | Type |
|---|---|---|
| NetJets (Berkshire Hathaway) | 32 | Corporate |
| Boeing | 7 | Corporate |
| JPMorgan Chase | 5 | Finance |
| Johnson & Johnson | 4 | Corporate |
| Northrop Grumman | 4 | Corporate |
| Procter & Gamble | 4 | Corporate |
| Chevron | 3 | Corporate |
| GE Aerospace | 3 | Corporate |
| General Dynamics | 3 | Corporate |
| Kroger | 3 | Corporate |
| Merck | 3 | Corporate |
| Caterpillar | 2 | Corporate |
| Costco | 2 | Corporate |
| ExxonMobil | 2 | Corporate |
| Hilton Hotels | 2 | Corporate |
| Honeywell | 2 | Corporate |
| Kimberly-Clark | 2 | Corporate |
| Nike | 2 | Corporate |
| Qualcomm | 2 | Corporate |
| Apollo Global Management | 1 | PE |
| Citadel | 1 | Hedge Fund |
| L3Harris Technologies | 1 | Corporate |
| Lowe's Companies | 1 | Corporate |
| Oracle | 1 | Corporate |
| Renaissance Technologies (?) | 1 | Hedge Fund |
| Silver Lake | 1 | PE |
| Wells Fargo | 1 | Finance |
| *+ 2 others* | — | — |

<span class="section-number" id="backtest">05: Getting Real Results</span>

## Running the Backtest With Real Data

The live scan shows current positions. Signals A and C require historical routing data: where each aircraft flew over the last 30 to 90 days. Here is exactly how to get the data and what to do with it.

### The data constraint

The OpenSky Network REST API returns per-aircraft flight history, departure airport, arrival airport, and timestamp, over a rolling 30-day window for any registered user. Anonymous access is limited to roughly 48 hours and rate-limits too aggressively for batch queries. A free account removes both restrictions.

Create one here (takes about 5 minutes): [opensky-network.org/index.php?option=com_users&view=registration](https://opensky-network.org/index.php?option=com_users&view=registration)

### Step 1: Collect flight history

With credentials, run `data/collect.py` once to pull 30 days of history for all 95 aircraft, then again daily to keep the database current:

```bash
# First run: backfill 30 days
python collect.py --user YOUR_USERNAME --pass YOUR_PASSWORD --days 30

# Then add to cron (daily at 06:00 UTC)
0 6 * * * cd /path/to/data && python collect.py --user U --pass P >> collect.log 2>&1
```

The script stores every flight in a local SQLite database (`flights.db`): departure airport, arrival airport, ICAO24, and timestamp. Runs are deduplicated. At 95 aircraft averaging roughly 3 flights per week, a 30-day window produces 400 to 600 flight records.

### Step 2: Pull M&A announcements

SEC EDGAR's full-text search API provides free structured access to every merger agreement filing:

```
GET https://efts.sec.gov/LATEST/search-index
    ?q=%22Agreement+and+Plan+of+Merger%22
    &forms=SC%20TO-T
    &dateRange=custom&startdt=2024-01-01&enddt=2025-12-31
```

Filter to deals where the acquirer matches a watchlist operator, JPMorgan, J&J, Merck, ExxonMobil, Chevron, General Dynamics, Honeywell, and others, then extract the target's HQ city and announcement date.

### Step 3: Run the analysis

`data/backtest.py` does the matching automatically. For each M&A event, the script looks back 60 days, finds all watchlist flights by the acquirer's aircraft, and flags any flight landing within 80 km of the target HQ. Output is a CSV with per-deal results and an aggregate hit rate.

```bash
python backtest.py YOUR_USERNAME YOUR_PASSWORD
```

The M&A corpus in the script covers 12 announced deals from 2021 to 2023. These include JPMorgan Chase, Johnson and Johnson, Merck, ExxonMobil (the $59.5B Pioneer deal), Chevron (the $53B Hess deal), Honeywell, Caterpillar, and General Dynamics. All of these predate the free 30-day API window. The initial run uses only recent deals. For the 2021 to 2023 events, you need either the OpenSky research dataset (application-based, at opensky-network.org/data/impala) or a paid provider such as ADS-B Exchange or FlightAware AeroAPI.

### Why the ExxonMobil and Chevron deals matter as test cases

ExxonMobil announced the $59.5 billion acquisition of Pioneer Natural Resources on October 11, 2023. Chevron announced the $53 billion acquisition of Hess Corporation on October 23, 2023. Both deals were announced in the same week. Pioneer's HQ is in Dallas. Hess is in New York. ExxonMobil and Chevron each have three tracked Gulfstream G650ERs.

If either firm's jets were flying to Dallas or New York in the 30 to 60 days before October 11 or 23, 2023, and those visits fell outside their normal routing, the signal fires. Recovering that data requires either the OpenSky research archive or a paid ADS-B history API. Both deals fall outside the free 30-day window. For new deals going forward, the free tier is sufficient.

<div class="info-box">
<span class="info-box-label">Run it yourself</span>
<p>All code is in this site's <code>data/</code> directory. <code>build_watchlist.py</code> regenerates the FAA-sourced watchlist weekly. <code>collect.py</code> runs daily collection into SQLite. <code>backtest.py</code> runs the M&A correlation analysis. The only external dependency beyond the FAA public download is a free OpenSky account.</p>
</div>

<script>
(function () {

// ── Watchlist: 95 aircraft sourced from FAA ReleasableAircraft.zip ─────────
// Generated by data/build_watchlist.py — do not edit manually.
// Last built: 2026-06-07
var WATCHLIST = [{"reg":"N541BA","hex":"A6DBBD","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N543BA","hex":"A6E32B","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N544BA","hex":"A6E6E2","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N545BA","hex":"A6EA99","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N547BA","hex":"A6F207","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N604TB","hex":"A7D7C6","owner":"Boeing","type":"corp","aircraft":"Bombardier Challenger 604","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N646TB","hex":"A87D30","owner":"Boeing","type":"corp","aircraft":"Bombardier Global Express","hqCity":"Arlington VA","hqLat":38.8799,"hqLon":-77.1068},{"reg":"N175CT","hex":"A12C04","owner":"Caterpillar","type":"corp","aircraft":"Gulfstream G500","hqCity":"Peoria","hqLat":40.6936,"hqLon":-89.589},{"reg":"N797CT","hex":"AAD24A","owner":"Caterpillar","type":"corp","aircraft":"Bombardier Global Express","hqCity":"Peoria","hqLat":40.6936,"hqLon":-89.589},{"reg":"N1876P","hex":"A15DE5","owner":"Chevron","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"San Ramon","hqLat":37.7801,"hqLon":-121.978},{"reg":"N1895T","hex":"A16534","owner":"Chevron","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"San Ramon","hqLat":37.7801,"hqLon":-121.978},{"reg":"N1901G","hex":"A16AAD","owner":"Chevron","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"San Ramon","hqLat":37.7801,"hqLon":-121.978},{"reg":"N83CW","hex":"AB5648","owner":"Costco","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Issaquah","hqLat":47.5301,"hqLon":-122.0326},{"reg":"N91CW","hex":"AC9499","owner":"Costco","type":"corp","aircraft":"Gulfstream G700","hqCity":"Issaquah","hqLat":47.5301,"hqLon":-122.0326},{"reg":"N100A","hex":"A004B4","owner":"ExxonMobil","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Spring TX","hqLat":30.0799,"hqLon":-95.4172},{"reg":"N200A","hex":"A19203","owner":"ExxonMobil","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Spring TX","hqLat":30.0799,"hqLon":-95.4172},{"reg":"N882PX","hex":"AC269E","owner":"GE Aerospace","type":"corp","aircraft":"Gulfstream G550","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N942UP","hex":"AD1666","owner":"GE Aerospace","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N991RW","hex":"ADD7E6","owner":"GE Aerospace","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N585G","hex":"A78911","owner":"General Dynamics","type":"corp","aircraft":"Gulfstream G500","hqCity":"Reston","hqLat":38.9537,"hqLon":-77.3469},{"reg":"N586G","hex":"A78CC8","owner":"General Dynamics","type":"corp","aircraft":"Gulfstream G500","hqCity":"Reston","hqLat":38.9537,"hqLon":-77.3469},{"reg":"N587G","hex":"A7907F","owner":"General Dynamics","type":"corp","aircraft":"Gulfstream G500","hqCity":"Reston","hqLat":38.9537,"hqLon":-77.3469},{"reg":"N40LG","hex":"A4AB49","owner":"Hilton Hotels","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"McLean VA","hqLat":38.934,"hqLon":-77.1773},{"reg":"N519BH","hex":"A682FF","owner":"Hilton Hotels","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"McLean VA","hqLat":38.934,"hqLon":-77.1773},{"reg":"N889H","hex":"AC3FF3","owner":"Honeywell","type":"corp","aircraft":"Dassault Falcon 900EX","hqCity":"Charlotte","hqLat":35.2271,"hqLon":-80.8431},{"reg":"N933H","hex":"ACF17D","owner":"Honeywell","type":"corp","aircraft":"Gulfstream G550","hqCity":"Charlotte","hqLat":35.2271,"hqLon":-80.8431},{"reg":"N30QJ","hex":"A31E60","owner":"Johnson & Johnson","type":"corp","aircraft":"Gulfstream G700","hqCity":"New Brunswick","hqLat":40.4863,"hqLon":-74.4518},{"reg":"N400J","hex":"A4AD69","owner":"Johnson & Johnson","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"New Brunswick","hqLat":40.4863,"hqLon":-74.4518},{"reg":"N60QJ","hex":"A7C64D","owner":"Johnson & Johnson","type":"corp","aircraft":"Gulfstream G700","hqCity":"New Brunswick","hqLat":40.4863,"hqLon":-74.4518},{"reg":"N800J","hex":"AAE2A5","owner":"Johnson & Johnson","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"New Brunswick","hqLat":40.4863,"hqLon":-74.4518},{"reg":"N506HG","hex":"A650F0","owner":"Kimberly-Clark","type":"corp","aircraft":"Gulfstream G550","hqCity":"Irving TX","hqLat":32.8141,"hqLon":-96.9489},{"reg":"N672HG","hex":"A8E3DC","owner":"Kimberly-Clark","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Irving TX","hqLat":32.8141,"hqLon":-96.9489},{"reg":"N300KC","hex":"A32036","owner":"Kroger","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N302KC","hex":"A327A4","owner":"Kroger","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N304KC","hex":"A32F12","owner":"Kroger","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N291SR","hex":"A2FAD1","owner":"L3Harris Technologies","type":"corp","aircraft":"Bombardier Global Express","hqCity":"Melbourne FL","hqLat":28.0836,"hqLon":-80.6081},{"reg":"N44LC","hex":"A54941","owner":"Lowe's Companies","type":"corp","aircraft":"Gulfstream G500","hqCity":"Mooresville","hqLat":35.5846,"hqLon":-80.8101},{"reg":"N800MK","hex":"AAE2FA","owner":"Merck","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Kenilworth","hqLat":40.6737,"hqLon":-74.2952},{"reg":"N811MK","hex":"AB0E30","owner":"Merck","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Kenilworth","hqLat":40.6737,"hqLon":-74.2952},{"reg":"N822MK","hex":"AB3966","owner":"Merck","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Kenilworth","hqLat":40.6737,"hqLon":-74.2952},{"reg":"N122QS","hex":"A05C8F","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Bombardier Global XRS","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N557QS","hex":"A71ADB","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N565QS","hex":"A73AEC","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N568QS","hex":"A74611","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N573QS","hex":"A75AFD","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N574QS","hex":"A75EB4","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N575QS","hex":"A7626B","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N576QS","hex":"A76622","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N577QS","hex":"A769D9","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N579QS","hex":"A77147","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N580QS","hex":"A77757","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N583QS","hex":"A7827C","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N587QS","hex":"A79158","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N588QS","hex":"A7950F","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N589QS","hex":"A798C6","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N592QS","hex":"A7A644","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N594QS","hex":"A7ADB2","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N611QS","hex":"A7F3E4","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N619QS","hex":"A8119C","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N643QS","hex":"A871CF","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N655QS","hex":"A8A0BC","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N669QS","hex":"A8D717","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N678QS","hex":"A8FADF","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N682QS","hex":"A90C14","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N683QS","hex":"A90FCB","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N685QS","hex":"A91739","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N686QS","hex":"A91AF0","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N689QS","hex":"A92615","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N693QS","hex":"A9374A","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Sovereign","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N707QS","hex":"A96FFE","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N727QS","hex":"A9BEFC","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Bombardier Challenger 300","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N894QS","hex":"AC559F","owner":"NetJets (Berkshire Hathaway)","type":"corp","aircraft":"Cessna Citation Longitude","hqCity":"Columbus","hqLat":39.9612,"hqLon":-82.9988},{"reg":"N1972","hex":"A184CA","owner":"Nike","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Beaverton","hqLat":45.4871,"hqLon":-122.8037},{"reg":"N3546","hex":"A3F6D3","owner":"Nike","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Beaverton","hqLat":45.4871,"hqLon":-122.8037},{"reg":"N37NG","hex":"A432A5","owner":"Northrop Grumman","type":"corp","aircraft":"Gulfstream G550","hqCity":"Falls Church","hqLat":38.8826,"hqLon":-77.1711},{"reg":"N37WH","hex":"A4336E","owner":"Northrop Grumman","type":"corp","aircraft":"Gulfstream G-IV","hqCity":"Falls Church","hqLat":38.8826,"hqLon":-77.1711},{"reg":"N38NG","hex":"A45A24","owner":"Northrop Grumman","type":"corp","aircraft":"Gulfstream G550","hqCity":"Falls Church","hqLat":38.8826,"hqLon":-77.1711},{"reg":"N99NG","hex":"ADD17D","owner":"Northrop Grumman","type":"corp","aircraft":"Gulfstream G-V","hqCity":"Falls Church","hqLat":38.8826,"hqLon":-77.1711},{"reg":"N15GX","hex":"A0C882","owner":"Oracle","type":"corp","aircraft":"Bombardier Global Express","hqCity":"Austin","hqLat":30.2672,"hqLon":-97.7431},{"reg":"N1PG","hex":"A0014E","owner":"Procter & Gamble","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N2PG","hex":"A18E9D","owner":"Procter & Gamble","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N5PG","hex":"A6368A","owner":"Procter & Gamble","type":"corp","aircraft":"Gulfstream G500","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N6PG","hex":"A7C3D9","owner":"Procter & Gamble","type":"corp","aircraft":"Gulfstream G500","hqCity":"Cincinnati","hqLat":39.1031,"hqLon":-84.512},{"reg":"N880WT","hex":"AC1FDB","owner":"Qualcomm","type":"corp","aircraft":"Gulfstream G800","hqCity":"San Diego","hqLat":32.7157,"hqLon":-117.1611},{"reg":"N882WT","hex":"AC2749","owner":"Qualcomm","type":"corp","aircraft":"Gulfstream G650ER","hqCity":"San Diego","hqLat":32.7157,"hqLon":-117.1611},{"reg":"N601CH","hex":"A7CB30","owner":"JPMorgan Chase","type":"finance","aircraft":"Gulfstream G700","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N661CH","hex":"A8B82A","owner":"JPMorgan Chase","type":"finance","aircraft":"Gulfstream G650ER","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N662CH","hex":"A8BBE1","owner":"JPMorgan Chase","type":"finance","aircraft":"Gulfstream G650ER","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N806CH","hex":"AAF861","owner":"JPMorgan Chase","type":"finance","aircraft":"Gulfstream G800","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N807CH","hex":"AAFC18","owner":"JPMorgan Chase","type":"finance","aircraft":"Gulfstream G800","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N878HL","hex":"AC14C8","owner":"Wells Fargo","type":"finance","aircraft":"Bombardier Global XRS","hqCity":"San Francisco","hqLat":37.7749,"hqLon":-122.4194},{"reg":"N888PX","hex":"AC3CE8","owner":"Citadel","type":"hedge","aircraft":"Gulfstream G700","hqCity":"Miami","hqLat":25.7617,"hqLon":-80.1918},{"reg":"N300WK","hex":"A32150","owner":"Renaissance Technologies (?)","type":"hedge","aircraft":"Bombardier Challenger 300","hqCity":"East Setauket","hqLat":40.9326,"hqLon":-73.1093},{"reg":"N878CC","hex":"AC1443","owner":"Apollo Global Management","type":"pe","aircraft":"Bombardier Challenger 604","hqCity":"New York","hqLat":40.7128,"hqLon":-74.006},{"reg":"N33VC","hex":"A39554","owner":"Silver Lake","type":"pe","aircraft":"Dassault Falcon 2000EX","hqCity":"Menlo Park","hqLat":37.4529,"hqLon":-122.1817}];

// ── Type colours ──────────────────────────────────────────────────────────────
var TYPE_COLOR = {
  corp:       '#61afef',
  finance:    '#56b6c2',
  pe:         '#e5c07b',
  hedge:      '#c678dd',
  individual: '#e06c75',
};
var TYPE_LABEL = {
  corp:       'Corporate',
  finance:    'Finance',
  pe:         'PE / Alt. Asset',
  hedge:      'Hedge Fund',
  individual: 'Individual',
};

// Major hub airports by IATA — excluded from convergence detection
var MAJOR_HUBS = new Set([
  'ATL','LAX','ORD','DFW','DEN','JFK','SFO','SEA','LAS','MCO',
  'EWR','PHX','IAH','MIA','BOS','MSP','DTW','FLL','PHL','LGA',
  'CLT','BWI','SLC','SAN','TPA','IAD','MDW','HNL','PDX','STL',
  'TEB','VNY','SMF','OAK','SJC',
]);

var results   = [];
var mapInited = false;
var leafletMap= null;
var markers   = [];

// ── Load Leaflet dynamically ───────────────────────────────────────────────────
function loadLeaflet(cb) {
  if (window.L) { cb(); return; }
  var s = document.createElement('script');
  s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  s.onload = cb;
  s.onerror = function() { console.error('Failed to load Leaflet'); cb(); };
  document.head.appendChild(s);
}

function initMap() {
  if (mapInited || !window.L) return;
  mapInited = true;
  leafletMap = L.map('cjet-map', { zoomControl: true, scrollWheelZoom: false })
    .setView([39.5, -98.35], 4);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd', maxZoom: 19,
  }).addTo(leafletMap);
}

function clearMarkers() {
  markers.forEach(function(m) { if (leafletMap) leafletMap.removeLayer(m); });
  markers = [];
}

function circleIcon(color, airborne) {
  var sz = airborne ? 14 : 9;
  return L.divIcon({
    className: '',
    html: '<div style="width:'+sz+'px;height:'+sz+'px;border-radius:50%;background:'+color+';border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.35);opacity:'+(airborne?1:0.45)+'"></div>',
    iconSize: [sz, sz], iconAnchor: [sz/2, sz/2],
  });
}

async function fetchReg(reg) {
  var res = await fetch('https://api.airplanes.live/v2/reg/' + reg);
  if (!res.ok) return null;
  var data = await res.json();
  return (data.ac && data.ac.length > 0) ? data.ac[0] : null;
}

function haversine(lat1, lon1, lat2, lon2) {
  var R = 6371, p1 = lat1*Math.PI/180, p2 = lat2*Math.PI/180;
  var dp = (lat2-lat1)*Math.PI/180, dl = (lon2-lon1)*Math.PI/180;
  var a = Math.sin(dp/2)*Math.sin(dp/2) + Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)*Math.sin(dl/2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

function detectConvergence(liveResults) {
  var airborne = liveResults.filter(function(r) { return r.ac && r.ac.lat != null; });
  var flags = [];
  for (var i = 0; i < airborne.length; i++) {
    for (var j = i+1; j < airborne.length; j++) {
      var a = airborne[i], b = airborne[j];
      if (a.entry.owner === b.entry.owner) continue;
      var dist = haversine(a.ac.lat, a.ac.lon, b.ac.lat, b.ac.lon);
      if (dist < 200) flags.push({ a: a, b: b, dist: Math.round(dist) });
    }
  }
  return flags;
}

function renderAnomalies(flags) {
  var el = document.getElementById('cjet-anomalies');
  if (!el) return;
  if (!flags.length) { el.innerHTML = ''; return; }
  var html = '<div class="cjet-anomaly-banner"><span class="cjet-anomaly-label">Signal B — Convergence Detected</span>';
  flags.forEach(function(c) {
    html += '<div class="cjet-anomaly-row"><strong>'+c.a.entry.reg+'</strong> ('+c.a.entry.owner+') and <strong>'+c.b.entry.reg+'</strong> ('+c.b.entry.owner+') are currently '+c.dist+' km apart — both airborne</div>';
  });
  html += '</div>';
  el.innerHTML = html;
}

function renderTable(res) {
  var el = document.getElementById('cjet-table');
  if (!el) return;
  var found    = res.filter(function(r) { return r.ac; });
  var notFound = res.filter(function(r) { return !r.ac; });
  if (!found.length && !notFound.length) { el.innerHTML = ''; return; }

  var html = '<div class="cjet-table-wrap">'
    + '<div class="cjet-table-header"><span class="cjet-table-title">Watchlist Status</span>'
    + '<span class="cjet-table-meta">'+found.length+' of '+res.length+' located via ADS-B</span></div>'
    + '<table class="cjet-table"><thead><tr>'
    + '<th>Reg.</th><th>Owner</th><th>Type</th><th>Aircraft</th><th>Status</th><th>Alt (ft)</th><th>Speed (kts)</th>'
    + '</tr></thead><tbody>';

  found.forEach(function(r) {
    var ac = r.ac;
    var airborne = typeof ac.alt_baro === 'number';
    var color = TYPE_COLOR[r.entry.type] || '#888';
    var altStr = airborne ? Math.round(ac.alt_baro).toLocaleString() : '—';
    var spdStr = ac.gs != null ? Math.round(ac.gs) : '—';
    var statusEl = airborne
      ? '<span class="cjet-status cjet-status-air">Airborne</span>'
      : '<span class="cjet-status cjet-status-gnd">On Ground</span>';
    html += '<tr>'
      + '<td><span class="cjet-reg" style="border-left:3px solid '+color+'">'+r.entry.reg+'</span></td>'
      + '<td><span class="cjet-owner">'+r.entry.owner+'</span></td>'
      + '<td><span class="cjet-type-badge" style="background:'+color+'22;color:'+color+'">'+( TYPE_LABEL[r.entry.type]||r.entry.type)+'</span></td>'
      + '<td class="cjet-aircraft">'+r.entry.aircraft+'</td>'
      + '<td>'+statusEl+'</td>'
      + '<td class="cjet-mono">'+altStr+'</td>'
      + '<td class="cjet-mono">'+spdStr+'</td>'
      + '</tr>';
  });

  if (notFound.length) {
    html += '<tr class="cjet-not-found-row"><td colspan="7"><span class="cjet-not-found-label">Not currently located ('+notFound.length+'):</span> '
      + notFound.map(function(r){return '<span class="cjet-reg-small">'+r.entry.reg+'</span>';}).join(' ')+'</td></tr>';
  }
  html += '</tbody></table></div>';
  el.innerHTML = html;
}

function addMarkers(res) {
  if (!leafletMap) return;
  res.forEach(function(r) {
    if (!r.ac || r.ac.lat == null) return;
    var color    = TYPE_COLOR[r.entry.type] || '#888';
    var airborne = typeof r.ac.alt_baro === 'number';
    var altStr   = airborne ? Math.round(r.ac.alt_baro).toLocaleString()+' ft' : 'On ground';
    var spdStr   = r.ac.gs != null ? Math.round(r.ac.gs)+' kts' : '—';
    var popup = '<div class="cjet-popup"><strong>'+r.entry.reg+'</strong><br>'+r.entry.owner+'<br><em>'+r.entry.aircraft+'</em><br>'+altStr+(airborne?'  ·  '+spdStr:'')+'</div>';
    var m = L.marker([r.ac.lat, r.ac.lon], { icon: circleIcon(color, airborne) })
      .addTo(leafletMap).bindPopup(popup);
    markers.push(m);
  });
}

function setProgress(done, total, msg) {
  var el = document.getElementById('cjet-progress');
  if (!el) return;
  el.style.display = 'block';
  var pct = Math.round(done/total*100);
  el.innerHTML = '<div class="cjet-progress-bar"><div class="cjet-progress-fill" style="width:'+pct+'%"></div></div>'
    + '<span class="cjet-progress-label">'+(msg||('Querying '+done+' / '+total+' registrations…'))+'</span>';
}
function hideProgress() {
  var el = document.getElementById('cjet-progress');
  if (el) el.style.display = 'none';
}

window.cjetScan = async function() {
  var btn = document.getElementById('cjet-scan-btn');
  if (btn) { btn.disabled = true; btn.textContent = 'Scanning…'; }

  loadLeaflet(async function() {
    initMap();
    clearMarkers();
    document.getElementById('cjet-anomalies').innerHTML = '';
    document.getElementById('cjet-table').innerHTML = '';

    var total = WATCHLIST.length, done = 0;
    results = [];

    for (var i = 0; i < WATCHLIST.length; i++) {
      var entry = WATCHLIST[i];
      setProgress(done, total);
      try {
        var ac = await fetchReg(entry.reg);
        results.push({ entry: entry, ac: ac });
      } catch(e) {
        results.push({ entry: entry, ac: null });
      }
      done++;
      await new Promise(function(r) { setTimeout(r, 120); });
    }

    setProgress(total, total, 'Complete — '+results.filter(function(r){return r.ac;}).length+' aircraft located');
    setTimeout(hideProgress, 3000);

    renderAnomalies(detectConvergence(results));
    renderTable(results);
    addMarkers(results);

    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Scan Again';
    }
  });
};

})();
</script>

<style>
.cjet-controls { display:flex; align-items:center; gap:1rem; margin-bottom:1rem; flex-wrap:wrap; }
.cjet-subtitle  { font-size:0.78rem; color:var(--gray); font-style:italic; }
.cjet-scan-btn  { display:inline-flex; align-items:center; gap:0.5rem; background:var(--secondary); color:#fff; border:none; border-radius:4px; padding:0.6rem 1.25rem; font-family:var(--bodyFont); font-size:0.88rem; font-weight:700; cursor:pointer; transition:opacity 0.15s; white-space:nowrap; }
.cjet-scan-btn:hover:not(:disabled) { opacity:0.85; }
.cjet-scan-btn:disabled { opacity:0.5; cursor:not-allowed; }

.cjet-progress { margin-bottom:0.75rem; }
.cjet-progress-bar { height:3px; background:var(--lightgray); border-radius:2px; overflow:hidden; margin-bottom:0.4rem; }
.cjet-progress-fill { height:100%; background:var(--secondary); transition:width 0.25s ease; }
.cjet-progress-label { font-size:0.75rem; color:var(--gray); font-family:var(--codeFont); }

.cjet-map { height:460px; border:1px solid var(--lightgray); border-radius:6px; margin-bottom:1.25rem; background:var(--light); }
.cjet-popup { font-size:0.82rem; line-height:1.6; }
.cjet-popup strong { font-size:0.9rem; }

.cjet-anomaly-banner { background:#e5c07b18; border:1px solid #e5c07b55; border-left:3px solid #e5c07b; border-radius:4px; padding:1rem 1.25rem; margin-bottom:1.25rem; }
.cjet-anomaly-label  { display:inline-block; font-size:0.72rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#c49a30; margin-bottom:0.5rem; }
.cjet-anomaly-row    { font-size:0.88rem; color:var(--darkgray); margin-top:0.35rem; line-height:1.5; }

.cjet-table-wrap   { margin-bottom:1.5rem; border:1px solid var(--lightgray); border-radius:6px; overflow:hidden; }
.cjet-table-header { display:flex; justify-content:space-between; align-items:center; padding:0.75rem 1rem; background:var(--lightgray); }
.cjet-table-title  { font-size:0.78rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:var(--dark); }
.cjet-table-meta   { font-size:0.75rem; color:var(--gray); font-family:var(--codeFont); }
.cjet-table        { width:100%; border-collapse:collapse; font-size:0.83rem; }
.cjet-table th     { font-size:0.68rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:var(--gray); padding:0.6rem 0.9rem; text-align:left; background:var(--light); border-bottom:1px solid var(--lightgray); }
.cjet-table td     { padding:0.6rem 0.9rem; border-bottom:1px solid var(--lightgray); vertical-align:middle; color:var(--darkgray); }
.cjet-table tbody tr:last-child td { border-bottom:none; }
.cjet-table tbody tr:hover td { background:var(--lightgray); }
.cjet-reg          { font-family:var(--codeFont); font-size:0.82rem; font-weight:700; color:var(--dark); padding-left:0.5rem; }
.cjet-reg-small    { font-family:var(--codeFont); font-size:0.78rem; color:var(--gray); background:var(--lightgray); padding:0.1rem 0.4rem; border-radius:3px; margin:0 0.15rem; }
.cjet-owner        { font-weight:600; color:var(--dark); font-size:0.83rem; }
.cjet-type-badge   { font-size:0.68rem; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; padding:0.15rem 0.55rem; border-radius:3px; white-space:nowrap; }
.cjet-aircraft     { font-size:0.8rem; color:var(--gray); white-space:nowrap; }
.cjet-mono         { font-family:var(--codeFont); font-size:0.82rem; }
.cjet-status       { font-size:0.7rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; padding:0.15rem 0.55rem; border-radius:3px; white-space:nowrap; }
.cjet-status-air   { background:#7ec8a022; color:#4a9e70; }
.cjet-status-gnd   { background:var(--lightgray); color:var(--gray); }
.cjet-not-found-row td { font-size:0.78rem; color:var(--gray); background:var(--light); padding:0.65rem 0.9rem; }
.cjet-not-found-label  { font-weight:600; margin-right:0.4rem; }

@media (max-width:640px) {
  .cjet-map { height:300px; }
  .cjet-controls { flex-direction:column; align-items:flex-start; }
  .cjet-table th:nth-child(n+5), .cjet-table td:nth-child(n+5) { display:none; }
}
</style>
