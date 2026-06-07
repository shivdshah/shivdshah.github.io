---
title: What's Flying Over You Right Now?
tags:
  - javascript
  - aviation
  - api
  - adsb
description: Live overhead aircraft tracker using ADS-B telemetry. No backend, no API keys, all client-side.
---

<div class="abstract">
<p>Enter your coordinates and a search radius to find the closest airborne aircraft overhead. The tool queries live ADS-B telemetry from ADSB.fi. No backend, no API keys, no server-side code. Everything runs in the browser.</p>
</div>

<span class="section-number">01: The Tool</span>

## Overhead Aircraft Lookup

<div class="flight-form">
<div class="flight-input-row">
<div class="flight-input-group">
<label for="fr-lat">Latitude</label>
<input type="number" id="fr-lat" placeholder="e.g. 51.5074" step="any" min="-90" max="90">
</div>
<div class="flight-input-group">
<label for="fr-lon">Longitude</label>
<input type="number" id="fr-lon" placeholder="e.g. -0.1278" step="any" min="-180" max="180">
</div>
<div class="flight-input-group">
<label for="fr-radius">Radius (km)</label>
<input type="number" id="fr-radius" value="50" min="5" max="250" step="5">
</div>
</div>
<button class="flight-locate-btn" id="fr-locate-btn" onclick="frUseLocation()">Use my location</button>
<button class="flight-btn" id="fr-btn" onclick="frRunLookup()">
<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
Find Closest Aircraft
</button>
</div>

<div id="fr-result"></div>

<span class="section-number">02: Technical Write-up</span>

## How It Works

This tool runs entirely in the browser. No backend, no API keys, no server-side code. Every result is assembled client-side from two open REST APIs: live radio telemetry and a crowd-sourced route database.

### ADS-B and ADSB.fi

Modern commercial aircraft continuously transmit their position using Automatic Dependent Surveillance-Broadcast (ADS-B). Unlike conventional secondary radar, which works by interrogating aircraft with a ground-based signal, ADS-B is unsolicited. The aircraft's onboard avionics derive a GPS fix and broadcast a 1090 MHz signal containing its ICAO address, barometric altitude, ground speed, track angle, and vertical rate roughly every 0.5 seconds. Any receiver within line-of-sight decodes it without coordination with the aircraft.

Airplanes.live is a free, community-operated ADS-B aggregator. Their public REST API sends `Access-Control-Allow-Origin: *` headers, making it suitable for direct browser calls with no server needed. A single request to `/v2/point/{lat}/{lon}/{radius}` returns the state vector for every tracked aircraft in the radius, including type code, registration, description, and distance from the query point.

### Step 1: Querying by Radius

The ADSB.fi endpoint takes a centre point and a radius in nautical miles directly, so no bounding-box conversion is needed. Your kilometre radius is converted before the request:

$$r_{\text{nm}} = \left\lceil \frac{r_{\text{km}}}{1.852} \right\rceil$$

The API returns every tracked aircraft within that radius, each with a `dst` field giving its distance from the query point in nautical miles. Aircraft flagged as on-ground (`alt_baro = "ground"`) are filtered out before ranking.

### Step 2: Finding the Closest Aircraft via Haversine

Aircraft are ranked by the `dst` field ADSB.fi provides. As a fallback, the Haversine formula computes the true great-circle distance for any aircraft missing a `dst` value:

$$a = \sin^2\!\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1\,\cos\phi_2\,\sin^2\!\left(\frac{\Delta\lambda}{2}\right)$$

$$d = 2R \arctan2\!\left(\sqrt{a},\;\sqrt{1-a}\right)$$

where $\phi$ and $\lambda$ are latitude and longitude in radians and $R = 6{,}371\,\text{km}$ is Earth's mean radius. The aircraft minimising $d$ is selected.

### Step 3: Enriching with Route Data

ADSB.fi returns the aircraft's ICAO type code, registration, and callsign directly. The one field it does not carry is the flight's route: origin and destination airports. For that, a second call goes to ADSBDB, a free crowd-sourced flight database:

| Endpoint | Data returned |
|---|---|
| `adsbdb.com/v0/callsign/{callsign}` | Airline name, origin airport (IATA), destination airport (IATA) |

ICAO aircraft type codes (`B77W`, `A21N`, `B38M`, etc.) are decoded to human-readable names via a local lookup table covering approximately 80 common types. `A21N`, for instance, maps to "Airbus A321neo".

### Unit Conversions

ADSB.fi returns values in aviation-standard units rather than SI, so only two conversions are needed:

| Field | ADSB.fi unit | Displayed as | Conversion |
|---|---|---|---|
| Altitude | feet (barometric) | feet | — |
| Ground speed | knots | mph | × 1.15078 |
| Vertical rate | ft/min | ft/s | ÷ 60 |
| Track | degrees true (N = 0°) | degrees + cardinal | — |

Barometric altitude is used rather than GPS geometric altitude because it is what ATC and pilots use operationally, referenced to the standard pressure datum of 1013.25 hPa.

### Limitations and Data Gaps

> [!note] Data availability
> Not all aircraft are visible. ADS-B equipage is mandatory for aircraft flying in controlled airspace above FL180 in most jurisdictions, but lighter general aviation, military, and some private charter operators are exempt or disable their transponder. ADSBDB route data is crowd-sourced and will be absent for cargo, positioning, or general aviation callsigns. In those cases the route fields display `???`.

<script>
(function () {
  // ── ICAO airline prefix (first 3 chars of callsign) → airline name ─────────
  var FR_AIRLINES = {
    AAL:'American Airlines', AAR:'Asiana Airlines', ACA:'Air Canada', ADH:'Air One',
    AEA:'Air Europa', AEE:'Aegean Airlines', AFR:'Air France', AHY:'Azerbaijan Airlines',
    AIB:'Air Berlin', AIC:'Air India', AKL:'Air Kilroe', ALK:'SriLankan Airlines',
    AMC:'Air Malta', AME:'Air Memphis', AMF:'Ameriquest Airlines', AMH:'Air Mauritanie',
    AMU:'Air Macau', AMX:'Aeromexico', ANA:'All Nippon Airways', ANZ:'Air New Zealand',
    APF:'Air Philippines', ARA:'Arik Air', ARE:'ASKY Airlines', ARI:'Air Serbia',
    ARN:'Aeronaves TSM', ATN:'Air Transport International', AUA:'Austrian Airlines',
    AVA:'Avianca', AXM:'AirAsia', AZA:'Alitalia', AZU:'Azul Airlines',
    BAW:'British Airways', BCS:'European Air Transport', BEE:'Flybe', BEL:'Brussels Airlines',
    BER:'Air Berlin', BMA:'British Midland', BPA:'Blue Panorama', BTI:'airBaltic',
    BWA:'Caribbean Airlines', CAI:'Corendon Airlines', CAL:'China Airlines',
    CCA:'Air China', CDG:'Shandong Airlines', CES:'China Eastern Airlines',
    CFG:'Condor', CHH:'Hainan Airlines', CKS:'Kalitta Air', CLH:'Lufthansa CityLine',
    CMP:'Copa Airlines', CNW:'Continental Micronesia', CSC:'Sichuan Airlines',
    CSH:'Shanghai Airlines', CSN:'China Southern Airlines', CSZ:'Shenzhen Airlines',
    CTN:'Croatia Airlines', CXA:'Xiamen Airlines', CXI:'SATA Air Açores',
    CYP:'Cyprus Airways', DAH:'Air Algérie', DAL:'Delta Air Lines',
    DAN:'Maersk Air', DLH:'Lufthansa', DLR:'Air Dolomiti',
    DSM:'Donbassaero', EAL:'Eastern Air Lines', EIN:'Aer Lingus',
    ELY:'El Al', ETE:'Ethiopian Airlines', ETD:'Etihad Airways',
    EXS:'Jet2', EZS:'easyJet Switzerland', EZY:'easyJet', FBU:'Flybus',
    FDX:'FedEx Express', FIN:'Finnair', FPO:'First Air', FUA:'Futura International Airways',
    GAO:'Garuda Indonesia', GEC:'Lufthansa Cargo', GFA:'Gulf Air',
    GIA:'Garuda Indonesia', GLO:'Gol Linhas Aéreas', GTI:'Atlas Air',
    HAL:'Hawaiian Airlines', HDA:'Dragonair', HHN:'Hahn Air', HVN:'Vietnam Airlines',
    IAW:'Iraqi Airways', IBE:'Iberia', ICE:'Icelandair', IGO:'IndiGo',
    IRA:'Iran Air', IRK:'Kish Air', ISS:'Meridiana', ITY:'ITA Airways',
    JAA:'Japan Asia Airways', JAI:'IndiGo', JAL:'Japan Airlines',
    JAT:'Air Serbia', JBU:'JetBlue', JKK:'Spanair', JSX:'JSX',
    KAL:'Korean Air', KAC:'Kuwait Airways', KLM:'KLM Royal Dutch Airlines',
    KQA:'Kenya Airways', KZR:'Air Astana', LAM:'LAM Mozambique Airlines',
    LAN:'LATAM Airlines', LAP:'LATAM Paraguay', LAO:'Lao Airlines',
    LDA:'Lauda', LGL:'Luxair', LHA:'Lufthansa', LOT:'LOT Polish Airlines',
    LRC:'LACSA', LSI:'Sky Airlines (Turkey)', LTU:'LTU International',
    MAH:'Malév Hungarian Airlines', MAU:'Air Mauritius', MAX:'Norwegian Air International',
    MAS:'Malaysia Airlines', MAY:'Malindo Air', MGL:'MIAT Mongolian Airlines',
    MHV:'MVair', MLD:'Air Moldova', MSR:'EgyptAir', MXD:'MaxAir',
    NAX:'Norwegian Air Shuttle', NCA:'Nippon Cargo Airlines', NKS:'Spirit Airlines',
    NLY:'Niki', NOZ:'Norwegian Air Sweden', NPT:'Nok Air',
    OAL:'Olympic Air', OMA:'Oman Air', OAW:'Helvetic Airways',
    PAC:'Polar Air Cargo', PAL:'Philippine Airlines', PAO:'Polynesian Airlines',
    PGA:'TAP Air Portugal', PKC:'Pakistan International Airlines', PLM:'Palma de Mallorca',
    QFA:'Qantas', QNA:'Swiftair', QNK:'Blue Islands', QTR:'Qatar Airways',
    RAM:'Royal Air Maroc', ROT:'TAROM', RUK:'Rwandair', RWD:'Air Rwanda',
    RYR:'Ryanair', SAA:'South African Airways', SAB:'Sabena',
    SAS:'Scandinavian Airlines', SAT:'SATA International', SBI:'S7 Airlines',
    SEY:'Air Seychelles', SHT:'British Airways (Shuttle)', SIA:'Singapore Airlines',
    SLM:'Surinam Airways', SNG:'SpiceJet', SOO:'Southern Air',
    SUD:'Sudan Airways', SVA:'Saudia', SWA:'Southwest Airlines',
    SWR:'Swiss International Air Lines', SXS:'Sun Express', SYR:'Syrian Air',
    TAM:'LATAM Brasil', TAP:'TAP Air Portugal', TAR:'Tunisair',
    THA:'Thai Airways', THT:'Air Tahiti Nui', THY:'Turkish Airlines',
    TOM:'TUI Airways', TRA:'Transavia', TUI:'TUI fly',
    TVF:'Transavia France', TWI:'Tailwind Airlines', TXI:'Texair',
    UAE:'Emirates', UAL:'United Airlines', UBD:'Wasaya Airways',
    UCA:'US Airways', UIA:'Ukraine International Airlines', UPS:'UPS Airlines',
    USA:'US Airways', VDA:'Volga-Dnepr Airlines', VIR:'Virgin Atlantic',
    VJC:'VietJet Air', VKG:'Thomas Cook Airlines Scandinavia', VLG:'Vueling',
    VOE:'Volotea', VOZ:'Virgin Australia', VRD:'Virgin America',
    VVB:'Viva Air', WDL:'WDL Aviation', WES:'West Air',
    WIF:'Wideroe', WJA:'WestJet', WOA:'World Airways',
    WZZ:'Wizz Air', XAX:'Xtra Airways', YZR:'Air Inuit',
  };

  function frAirlineName(callsign) {
    if (!callsign || callsign.length < 3) return null;
    var prefix = callsign.substring(0, 3).toUpperCase();
    return FR_AIRLINES[prefix] || null;
  }

  // ── ICAO type code → readable aircraft name ────────────────────────────────
  var FR_TYPES = {
    A318:'Airbus A318', A319:'Airbus A319', A320:'Airbus A320', A321:'Airbus A321',
    A18N:'Airbus A318neo', A19N:'Airbus A319neo', A20N:'Airbus A320neo', A21N:'Airbus A321neo',
    A332:'Airbus A330-200', A333:'Airbus A330-300', A338:'Airbus A330-800neo', A339:'Airbus A330-900neo',
    A342:'Airbus A340-200', A343:'Airbus A340-300', A345:'Airbus A340-500', A346:'Airbus A340-600',
    A359:'Airbus A350-900', A35K:'Airbus A350-1000', A388:'Airbus A380-800',
    B733:'Boeing 737-300', B734:'Boeing 737-400', B735:'Boeing 737-500',
    B736:'Boeing 737-600', B737:'Boeing 737-700', B738:'Boeing 737-800', B739:'Boeing 737-900',
    B38M:'Boeing 737 MAX 8', B39M:'Boeing 737 MAX 9', B3XM:'Boeing 737 MAX 10', B7M7:'Boeing 737 MAX 7',
    B742:'Boeing 747-200', B743:'Boeing 747-300', B744:'Boeing 747-400', B748:'Boeing 747-8I',
    B752:'Boeing 757-200', B753:'Boeing 757-300',
    B762:'Boeing 767-200', B763:'Boeing 767-300', B764:'Boeing 767-400',
    B772:'Boeing 777-200', B77L:'Boeing 777-200LR', B773:'Boeing 777-300', B77W:'Boeing 777-300ER',
    B778:'Boeing 777X-8', B779:'Boeing 777X-9',
    B788:'Boeing 787-8', B789:'Boeing 787-9', B78X:'Boeing 787-10',
    E135:'Embraer ERJ-135', E145:'Embraer ERJ-145',
    E170:'Embraer E170', E175:'Embraer E175', E190:'Embraer E190', E195:'Embraer E195',
    E75L:'Embraer E175-E2', E19E:'Embraer E190-E2', E29E:'Embraer E195-E2',
    CRJ1:'Bombardier CRJ-100', CRJ2:'Bombardier CRJ-200', CRJ7:'Bombardier CRJ-700',
    CRJ9:'Bombardier CRJ-900', CRJX:'Bombardier CRJ-1000',
    DH8A:'Bombardier Dash 8-100', DH8C:'Bombardier Dash 8-300', DH8D:'Bombardier Q400',
    AT43:'ATR 42-300', AT45:'ATR 42-500', AT46:'ATR 42-600',
    AT72:'ATR 72-200', AT75:'ATR 72-500', AT76:'ATR 72-600',
    MD11:'McDonnell Douglas MD-11', MD82:'MD-82', MD83:'MD-83', MD88:'MD-88', MD90:'MD-90',
    GL5T:'Bombardier Global 5000', GLEX:'Bombardier Global Express',
    G280:'Gulfstream G280', G550:'Gulfstream G550', G650:'Gulfstream G650',
    F900:'Dassault Falcon 900', F2TH:'Dassault Falcon 2000', F7X:'Dassault Falcon 7X',
    CL60:'Bombardier Challenger 600', CL65:'Bombardier Challenger 650',
    LJ45:'Learjet 45', LJ60:'Learjet 60', LJ75:'Learjet 75',
    H25B:'Hawker 800', BE40:'Beechjet 400', C56X:'Cessna Citation Excel',
    C172:'Cessna 172', C182:'Cessna 182', C208:'Cessna 208 Caravan',
    PA28:'Piper Cherokee', PC12:'Pilatus PC-12', SR22:'Cirrus SR22',
    F100:'Fokker 100', F70:'Fokker 70', SF34:'Saab 340', SU95:'Sukhoi Superjet 100',
  };

  function frModel(code) {
    if (!code) return null;
    return FR_TYPES[code.toUpperCase()] || code.toUpperCase();
  }

  function frHaversine(lat1, lon1, lat2, lon2) {
    var R = 6371;
    var p1 = lat1 * Math.PI / 180, p2 = lat2 * Math.PI / 180;
    var dp = (lat2 - lat1) * Math.PI / 180, dl = (lon2 - lon1) * Math.PI / 180;
    var a = Math.sin(dp/2)*Math.sin(dp/2) + Math.cos(p1) * Math.cos(p2) * Math.sin(dl/2)*Math.sin(dl/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function frCardinal(deg) {
    if (deg == null) return '';
    var dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
    return dirs[Math.round(deg / 22.5) % 16];
  }

  function frSetStatus(msg, isError) {
    var el = document.getElementById('fr-result');
    if (el) el.innerHTML = '<p class="flight-status' + (isError ? ' error' : '') + '">' + msg + '</p>';
  }

  function frSetLoading(on) {
    var btn = document.getElementById('fr-btn');
    if (!btn) return;
    if (on) {
      btn.disabled = true;
      btn.innerHTML = '<div class="flight-spinner"></div> Querying…';
    } else {
      btn.disabled = false;
      btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Find Closest Aircraft';
    }
  }

  function frRender(d) {
    var altStr = d.altFt  != null ? Math.round(d.altFt).toLocaleString()  : '—';
    var spdStr = d.spdMph != null ? Math.round(d.spdMph).toLocaleString() : '—';
    var trkStr = d.track  != null ? Math.round(d.track) + '°'        : '—';
    var trkSub = d.track  != null ? frCardinal(d.track) : '';

    var vrStr, vrClass, vrSub;
    if (d.vrFps != null) {
      vrStr   = (d.vrFps > 0 ? '+' : '') + d.vrFps.toFixed(1);
      vrClass = d.vrFps >  0.5 ? ' flight-vr-climb' : d.vrFps < -0.5 ? ' flight-vr-desc' : '';
      vrSub   = d.vrFps >  0.5 ? 'climbing' : d.vrFps < -0.5 ? 'descending' : 'level';
    } else {
      vrStr = '—'; vrClass = ''; vrSub = 'ft/s';
    }

    var routeStr;
    if (d.origin === '???' && d.dest === '???') {
      routeStr = '<em style="color:var(--gray)">Route unavailable</em>';
    } else if (d.origin === '???' || d.dest === '???') {
      var known = d.origin !== '???' ? (d.originName ? d.originName + ' (' + d.origin + ')' : d.origin) : (d.destName ? d.destName + ' (' + d.dest + ')' : d.dest);
      routeStr = '<em style="color:var(--gray)">' + (d.origin !== '???' ? known + '  →  ?' : '?  →  ' + known) + '</em>';
    } else {
      var o    = d.originName ? d.originName + ' (' + d.origin + ')' : d.origin;
      var dest = d.destName   ? d.destName   + ' (' + d.dest   + ')' : d.dest;
      routeStr = o + '  →  ' + dest;
    }

    var distStr = d.distance != null ? d.distance.toFixed(1) + ' km away' : '';

    var el = document.getElementById('fr-result');
    if (!el) return;
    el.innerHTML =
      '<div class="flight-result-card">' +
        '<div class="flight-result-header">' +
          '<div>' +
            '<span class="flight-callsign">' + (d.callsign || 'No callsign') + '</span>' +
            '<span class="flight-airline">' + d.airline + '</span>' +
            '<span class="flight-route">' + routeStr + '</span>' +
          '</div>' +
          (distStr ? '<span class="flight-dist-badge">↔ ' + distStr + '</span>' : '') +
        '</div>' +
        '<hr class="flight-divider">' +
        '<div class="flight-meta-row">' +
          '<div class="flight-meta-item"><span class="flight-meta-label">Aircraft</span><span class="flight-meta-value">' + d.model + '</span></div>' +
          '<div class="flight-meta-item"><span class="flight-meta-label">Reg.</span><span class="flight-meta-value">' + d.registration + '</span></div>' +
        '</div>' +
        '<div class="flight-stat-grid">' +
          '<div class="flight-stat-card"><span class="stat-label">Altitude</span><span class="stat-value">' + altStr + '</span><span class="stat-sub">feet</span></div>' +
          '<div class="flight-stat-card"><span class="stat-label">Speed</span><span class="stat-value">' + spdStr + '</span><span class="stat-sub">mph</span></div>' +
          '<div class="flight-stat-card"><span class="stat-label">Track</span><span class="stat-value">' + trkStr + '</span><span class="stat-sub">' + trkSub + '</span></div>' +
          '<div class="flight-stat-card"><span class="stat-label">Vert. Rate</span><span class="stat-value' + vrClass + '">' + vrStr + '</span><span class="stat-sub">' + vrSub + '</span></div>' +
        '</div>' +
        '<p class="flight-footer">' + d.totalAirborne + ' airborne aircraft in range</p>' +
      '</div>';
  }

  window.frUseLocation = function () {
    if (!navigator.geolocation) {
      frSetStatus('⚠ Geolocation is not supported by your browser.', true);
      return;
    }
    var btn = document.getElementById('fr-locate-btn');
    if (btn) btn.textContent = 'Getting location…';
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        document.getElementById('fr-lat').value = pos.coords.latitude.toFixed(4);
        document.getElementById('fr-lon').value = pos.coords.longitude.toFixed(4);
        if (btn) { btn.textContent = '✓ Location set'; setTimeout(function () { btn.textContent = 'Use my location'; }, 2000); }
      },
      function (err) {
        if (btn) btn.textContent = 'Use my location';
        frSetStatus('⚠ Location access denied. Enter coordinates manually.', true);
      }
    );
  };

  window.frRunLookup = async function () {
    var lat    = parseFloat(document.getElementById('fr-lat').value);
    var lon    = parseFloat(document.getElementById('fr-lon').value);
    var radius = parseFloat(document.getElementById('fr-radius').value);

    if (isNaN(lat)    || lat < -90  || lat > 90)   { frSetStatus('⚠ Enter a valid latitude (−90 to 90).', true);    return; }
    if (isNaN(lon)    || lon < -180 || lon > 180)  { frSetStatus('⚠ Enter a valid longitude (−180 to 180).', true); return; }
    if (isNaN(radius) || radius <= 0)              { frSetStatus('⚠ Enter a positive search radius in km.', true);       return; }

    frSetLoading(true);
    frSetStatus('Querying ADSB.fi…');

    try {
      // ADSB.fi uses nautical miles
      var radiusNm = Math.max(1, Math.ceil(radius / 1.852));

      var res = await fetch(
        'https://api.airplanes.live/v2/point/' + lat + '/' + lon + '/' + radiusNm
      );
      if (!res.ok) throw new Error('API returned HTTP ' + res.status + '. Try again shortly.');

      var data = await res.json();

      if (!data.ac || data.ac.length === 0)
        throw new Error('No aircraft detected in that area. Try a larger radius or a different location.');

      // Filter to airborne aircraft with known positions
      var airborne = data.ac.filter(function (a) {
        return typeof a.alt_baro === 'number' && a.lat != null && a.lon != null;
      });

      if (airborne.length === 0)
        throw new Error(data.ac.length + ' aircraft found but all appear to be on the ground.');

      // Sort by distance (dst in nautical miles; fall back to haversine)
      airborne.sort(function (a, b) {
        var da = a.dst != null ? a.dst : frHaversine(lat, lon, a.lat, a.lon) / 1.852;
        var db = b.dst != null ? b.dst : frHaversine(lat, lon, b.lat, b.lon) / 1.852;
        return da - db;
      });

      var closest  = airborne[0];
      var callsign = (closest.flight || '').trim().replace(/\s+/g, '');
      var distKm   = closest.dst != null
        ? closest.dst * 1.852
        : frHaversine(lat, lon, closest.lat, closest.lon);
      // airplanes.live provides a plain-English desc (e.g. "Boeing 737-800"), prefer over type code lookup
      var modelName = closest.desc || frModel(closest.t) || '—';

      frSetStatus('Fetching route details…');

      // ADSBDB route lookup
      var route = null;
      if (callsign) {
        try {
          var rRes = await fetch('https://api.adsbdb.com/v0/callsign/' + callsign);
          if (rRes.ok) {
            var rData = await rRes.json();
            route = rData && rData.response && rData.response.flightroute;
          }
        } catch (e) { /* route unavailable */ }
      }

      // ADSB.fi: alt_baro in feet, gs in knots, baro_rate in ft/min
      frRender({
        callsign:      callsign,
        airline:       (route && route.airline && route.airline.name) || frAirlineName(callsign) || 'Unknown',
        origin:        (route && route.origin      && route.origin.iata_code)           || '???',
        originName:    (route && route.origin      && route.origin.name)                || '',
        dest:          (route && route.destination && route.destination.iata_code)      || '???',
        destName:      (route && route.destination && route.destination.name)           || '',
        model:         modelName,
        registration:  closest.r || (closest.hex && closest.hex.toUpperCase()) || '—',
        altFt:         closest.alt_baro,
        spdMph:        closest.gs        != null ? closest.gs        * 1.15078 : null,
        track:         closest.track     != null ? closest.track               : null,
        vrFps:         closest.baro_rate != null ? closest.baro_rate / 60      : null,
        distance:      distKm,
        totalAirborne: airborne.length,
      });

    } catch (err) {
      frSetStatus('⚠ ' + (err.message || 'Something went wrong. Please try again.'), true);
    } finally {
      frSetLoading(false);
    }
  };

  // Enter key inside the form submits
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target && e.target.closest && e.target.closest('.flight-form')) {
      window.frRunLookup();
    }
  });
})();
</script>
