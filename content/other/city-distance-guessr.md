---
title: "City Distance Guessr"
tags:
  - game
  - geography
  - interactive
description: Guess the great-circle distance between two cities. Five rounds, score up to 1000 per round.
---

<div id="cdg-root">
  <div id="cdg-header">
    <span id="cdg-progress"></span>
    <button id="cdg-unit-toggle" onclick="cdgToggleUnit()">km / mi</button>
  </div>
  <div id="cdg-body"></div>
</div>

<script>
(function () {

var PAIRS = [
  // ── EASY (30) ─────────────────────────────────────────────────────────────
  { city1: "London",        city2: "New York",      distanceKm: 5570  },
  { city1: "Paris",         city2: "Berlin",        distanceKm: 878   },
  { city1: "Los Angeles",   city2: "New York",      distanceKm: 3940  },
  { city1: "Sydney",        city2: "Melbourne",     distanceKm: 714   },
  { city1: "Tokyo",         city2: "Beijing",       distanceKm: 2100  },
  { city1: "Rome",          city2: "Madrid",        distanceKm: 1365  },
  { city1: "Moscow",        city2: "London",        distanceKm: 2500  },
  { city1: "Cairo",         city2: "Jerusalem",     distanceKm: 424   },
  { city1: "Toronto",       city2: "Chicago",       distanceKm: 703   },
  { city1: "Amsterdam",     city2: "Brussels",      distanceKm: 174   },
  { city1: "Madrid",        city2: "Lisbon",        distanceKm: 502   },
  { city1: "Vienna",        city2: "Prague",        distanceKm: 252   },
  { city1: "Dubai",         city2: "Mumbai",        distanceKm: 1929  },
  { city1: "Singapore",     city2: "Kuala Lumpur",  distanceKm: 350   },
  { city1: "São Paulo",     city2: "Buenos Aires",  distanceKm: 1757  },
  { city1: "Tokyo",         city2: "Seoul",         distanceKm: 1157  },
  { city1: "Bangkok",       city2: "Singapore",     distanceKm: 1433  },
  { city1: "Paris",         city2: "London",        distanceKm: 341   },
  { city1: "New York",      city2: "Miami",         distanceKm: 1757  },
  { city1: "Sydney",        city2: "Auckland",      distanceKm: 2157  },
  { city1: "Beijing",       city2: "Shanghai",      distanceKm: 1068  },
  { city1: "Istanbul",      city2: "Athens",        distanceKm: 681   },
  { city1: "Vancouver",     city2: "Seattle",       distanceKm: 226   },
  { city1: "Cairo",         city2: "Dubai",         distanceKm: 2412  },
  { city1: "Mexico City",   city2: "Los Angeles",   distanceKm: 2487  },
  { city1: "Frankfurt",     city2: "Warsaw",        distanceKm: 925   },
  { city1: "Stockholm",     city2: "Oslo",          distanceKm: 416   },
  { city1: "London",        city2: "Dublin",        distanceKm: 464   },
  { city1: "Copenhagen",    city2: "Hamburg",       distanceKm: 285   },
  { city1: "Zurich",        city2: "Munich",        distanceKm: 244   },

  // ── MEDIUM (35) ───────────────────────────────────────────────────────────
  { city1: "Nairobi",       city2: "Mumbai",        distanceKm: 4431  },
  { city1: "Sydney",        city2: "Tokyo",         distanceKm: 7823  },
  { city1: "Lagos",         city2: "Johannesburg",  distanceKm: 4470  },
  { city1: "Cairo",         city2: "Nairobi",       distanceKm: 3658  },
  { city1: "Delhi",         city2: "Singapore",     distanceKm: 4151  },
  { city1: "Jakarta",       city2: "Sydney",        distanceKm: 5556  },
  { city1: "Chicago",       city2: "London",        distanceKm: 6350  },
  { city1: "São Paulo",     city2: "Lagos",         distanceKm: 6147  },
  { city1: "Moscow",        city2: "Beijing",       distanceKm: 5784  },
  { city1: "Karachi",       city2: "Nairobi",       distanceKm: 4016  },
  { city1: "Lima",          city2: "Miami",         distanceKm: 4748  },
  { city1: "Toronto",       city2: "London",        distanceKm: 5726  },
  { city1: "Istanbul",      city2: "Dubai",         distanceKm: 2949  },
  { city1: "Johannesburg",  city2: "Mumbai",        distanceKm: 6262  },
  { city1: "Casablanca",    city2: "São Paulo",     distanceKm: 7836  },
  { city1: "Bogotá",        city2: "Madrid",        distanceKm: 8047  },
  { city1: "Seoul",         city2: "Los Angeles",   distanceKm: 9620  },
  { city1: "Nairobi",       city2: "London",        distanceKm: 6823  },
  { city1: "Mumbai",        city2: "London",        distanceKm: 7197  },
  { city1: "Ho Chi Minh",   city2: "Sydney",        distanceKm: 7416  },
  { city1: "Algiers",       city2: "Paris",         distanceKm: 1344  },
  { city1: "Accra",         city2: "Rio de Janeiro",distanceKm: 5729  },
  { city1: "Dhaka",         city2: "Tokyo",         distanceKm: 5293  },
  { city1: "Riyadh",        city2: "London",        distanceKm: 5125  },
  { city1: "Manila",        city2: "Tokyo",         distanceKm: 2996  },
  { city1: "Santiago",      city2: "New York",      distanceKm: 8260  },
  { city1: "Lagos",         city2: "London",        distanceKm: 5079  },
  { city1: "Colombo",       city2: "Singapore",     distanceKm: 2390  },
  { city1: "Addis Ababa",   city2: "Dubai",         distanceKm: 2959  },
  { city1: "Casablanca",    city2: "London",        distanceKm: 2087  },
  { city1: "Almaty",        city2: "Moscow",        distanceKm: 2928  },
  { city1: "Kathmandu",     city2: "Beijing",       distanceKm: 3803  },
  { city1: "Luanda",        city2: "São Paulo",     distanceKm: 7256  },
  { city1: "Kyiv",          city2: "Moscow",        distanceKm: 756   },
  { city1: "Tehran",        city2: "Moscow",        distanceKm: 2809  },

  // ── HARD (30) ─────────────────────────────────────────────────────────────
  { city1: "Ulaanbaatar",   city2: "Lima",          distanceKm: 17540 },
  { city1: "Reykjavik",     city2: "Johannesburg",  distanceKm: 13898 },
  { city1: "Anchorage",     city2: "Dubai",         distanceKm: 10122 },
  { city1: "Honolulu",      city2: "London",        distanceKm: 11623 },
  { city1: "Ushuaia",       city2: "Tromsø",        distanceKm: 15034 },
  { city1: "Ulaanbaatar",   city2: "Buenos Aires",  distanceKm: 18279 },
  { city1: "Noumea",        city2: "Madrid",        distanceKm: 18079 },
  { city1: "Reykjavik",     city2: "Wellington",    distanceKm: 18548 },
  { city1: "Nuuk",          city2: "Tokyo",         distanceKm: 9413  },
  { city1: "Tashkent",      city2: "São Paulo",     distanceKm: 12613 },
  { city1: "Ashgabat",      city2: "Santiago",      distanceKm: 15803 },
  { city1: "Maputo",        city2: "Vancouver",     distanceKm: 17014 },
  { city1: "Ndjamena",      city2: "Manila",        distanceKm: 11285 },
  { city1: "Antananarivo",  city2: "Mexico City",   distanceKm: 17249 },
  { city1: "Ulaanbaatar",   city2: "Dakar",         distanceKm: 11327 },
  { city1: "Pyongyang",     city2: "Havana",        distanceKm: 14220 },
  { city1: "Baku",          city2: "Lima",          distanceKm: 14195 },
  { city1: "Yerevan",       city2: "Auckland",      distanceKm: 16993 },
  { city1: "Harare",        city2: "Anchorage",     distanceKm: 15218 },
  { city1: "Ouagadougou",   city2: "Bangkok",       distanceKm: 10015 },
  { city1: "Minsk",         city2: "Nairobi",       distanceKm: 6353  },
  { city1: "Tbilisi",       city2: "Buenos Aires",  distanceKm: 13734 },
  { city1: "Bishkek",       city2: "Cape Town",     distanceKm: 11153 },
  { city1: "Chisinau",      city2: "Bogotá",        distanceKm: 10164 },
  { city1: "Libreville",    city2: "Seoul",         distanceKm: 13247 },
  { city1: "Windhoek",      city2: "Tokyo",         distanceKm: 14016 },
  { city1: "Lusaka",        city2: "Vancouver",     distanceKm: 16085 },
  { city1: "Conakry",       city2: "Jakarta",       distanceKm: 12958 },
  { city1: "Bamako",        city2: "Hanoi",         distanceKm: 11009 },
  { city1: "Paramaribo",    city2: "Dhaka",         distanceKm: 14116 },
];

var TOTAL_ROUNDS = 5;
var unit = 'km';
var gameState = null;

function toDisplay(km) {
  return unit === 'km' ? km : Math.round(km * 0.621371);
}

function fromDisplay(val) {
  return unit === 'km' ? val : val / 0.621371;
}

function unitLabel() {
  return unit === 'km' ? 'km' : 'mi';
}

function score(guessKm, actualKm) {
  return Math.max(0, 1000 - Math.floor(Math.abs(guessKm - actualKm) / actualKm * 1000));
}

function accuracy(guessKm, actualKm) {
  var ratio = Math.abs(guessKm - actualKm) / actualKm;
  if (ratio <= 0.1) return 'great';
  if (ratio <= 0.3) return 'ok';
  return 'bad';
}

function shuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function startGame() {
  var shuffled = shuffle(PAIRS);
  gameState = {
    pairs: shuffled.slice(0, TOTAL_ROUNDS),
    round: 0,
    scores: [],
    revealed: false,
  };
  renderRound();
}

function renderProgress() {
  var el = document.getElementById('cdg-progress');
  if (!el) return;
  if (!gameState) { el.textContent = ''; return; }
  el.textContent = 'Round ' + (gameState.round + 1) + ' / ' + TOTAL_ROUNDS;
}

function renderRound() {
  renderProgress();
  var pair = gameState.pairs[gameState.round];
  var body = document.getElementById('cdg-body');
  if (!body) return;
  gameState.revealed = false;

  body.innerHTML =
    '<div class="cdg-pair">' + pair.city1 + ' → ' + pair.city2 + '</div>' +
    '<div class="cdg-guess-row">' +
      '<input id="cdg-input" class="cdg-input" type="number" min="0" placeholder="Distance in ' + unitLabel() + '" autofocus>' +
      '<button class="cdg-btn" onclick="cdgSubmit()">Submit</button>' +
    '</div>' +
    '<div id="cdg-result"></div>';

  var inp = document.getElementById('cdg-input');
  if (inp) inp.addEventListener('keydown', function(e) { if (e.key === 'Enter') cdgSubmit(); });
}

function cdgSubmit() {
  if (gameState.revealed) return;
  var inp = document.getElementById('cdg-input');
  if (!inp) return;
  var displayVal = parseFloat(inp.value);
  if (!displayVal || displayVal <= 0) { inp.focus(); return; }
  var guessKm = fromDisplay(displayVal);
  var pair = gameState.pairs[gameState.round];
  var pts = score(guessKm, pair.distanceKm);
  var acc = accuracy(guessKm, pair.distanceKm);
  gameState.scores.push(pts);
  gameState.revealed = true;

  var actualDisplay = toDisplay(pair.distanceKm);
  var guessDisplay = Math.round(displayVal);
  var maxDisplay = Math.max(actualDisplay, guessDisplay);

  var guessPct  = Math.round((guessDisplay  / maxDisplay) * 100);
  var actualPct = Math.round((actualDisplay / maxDisplay) * 100);

  var barColor = acc === 'great' ? '#22c55e' : acc === 'ok' ? '#f59e0b' : '#ef4444';

  var resultEl = document.getElementById('cdg-result');
  if (!resultEl) return;

  var isLast = gameState.round === TOTAL_ROUNDS - 1;
  var nextBtn = isLast
    ? '<button class="cdg-btn" onclick="cdgFinish()">See final score</button>'
    : '<button class="cdg-btn" onclick="cdgNext()">Next round</button>';

  resultEl.innerHTML =
    '<div class="cdg-reveal">' +
      '<div class="cdg-score-line"><span class="cdg-pts" style="color:' + barColor + '">' + pts + '</span><span class="cdg-pts-label"> pts</span></div>' +
      '<div class="cdg-bar-wrap">' +
        '<div class="cdg-bar-row">' +
          '<span class="cdg-bar-label">Your guess</span>' +
          '<div class="cdg-bar-track">' +
            '<div class="cdg-bar-fill cdg-bar-guess" style="width:' + guessPct + '%;background:' + barColor + '"></div>' +
          '</div>' +
          '<span class="cdg-bar-val">' + guessDisplay.toLocaleString() + ' ' + unitLabel() + '</span>' +
        '</div>' +
        '<div class="cdg-bar-row">' +
          '<span class="cdg-bar-label">Actual</span>' +
          '<div class="cdg-bar-track">' +
            '<div class="cdg-bar-fill cdg-bar-actual" style="width:' + actualPct + '%"></div>' +
          '</div>' +
          '<span class="cdg-bar-val">' + actualDisplay.toLocaleString() + ' ' + unitLabel() + '</span>' +
        '</div>' +
      '</div>' +
      '<div class="cdg-next-wrap">' + nextBtn + '</div>' +
    '</div>';
}

function cdgNext() {
  gameState.round++;
  renderRound();
}

function cdgFinish() {
  renderProgress();
  var total = gameState.scores.reduce(function(a, b) { return a + b; }, 0);
  var maxPossible = TOTAL_ROUNDS * 1000;
  var pct = Math.round(total / maxPossible * 100);
  var comment = pct >= 80 ? 'Exceptional geography knowledge.' : pct >= 55 ? 'Solid sense of the globe.' : pct >= 30 ? 'Room to explore the map more.' : 'The world is vast — keep exploring.';
  var body = document.getElementById('cdg-body');
  if (!body) return;

  var rows = gameState.scores.map(function(s, i) {
    var p = gameState.pairs[i];
    var col = s >= 800 ? '#22c55e' : s >= 400 ? '#f59e0b' : '#ef4444';
    return '<tr><td>' + p.city1 + ' → ' + p.city2 + '</td><td style="color:' + col + ';font-weight:600;text-align:right">' + s + '</td></tr>';
  }).join('');

  body.innerHTML =
    '<div class="cdg-final">' +
      '<div class="cdg-final-score">' + total + '<span class="cdg-final-max"> / ' + maxPossible + '</span></div>' +
      '<div class="cdg-final-comment">' + comment + '</div>' +
      '<table class="cdg-summary-table"><tbody>' + rows + '</tbody></table>' +
      '<button class="cdg-btn cdg-btn-wide" onclick="cdgRestart()">Play again</button>' +
    '</div>';

  var prog = document.getElementById('cdg-progress');
  if (prog) prog.textContent = 'Final score';
}

function cdgRestart() {
  startGame();
}

window.cdgToggleUnit = function() {
  unit = unit === 'km' ? 'mi' : 'km';
  var toggle = document.getElementById('cdg-unit-toggle');
  if (toggle) toggle.textContent = unit === 'km' ? 'km / mi' : 'mi / km';

  if (!gameState || gameState.revealed) {
    var inp = document.getElementById('cdg-input');
    if (inp) inp.placeholder = 'Distance in ' + unitLabel();
  }
};

window.cdgSubmit = cdgSubmit;
window.cdgNext   = cdgNext;
window.cdgFinish = cdgFinish;
window.cdgRestart = cdgRestart;

startGame();

})();
</script>

<style>
#cdg-root {
  font-family: var(--bodyFont);
  max-width: 560px;
}

#cdg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

#cdg-progress {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--gray);
}

#cdg-unit-toggle {
  font-family: var(--bodyFont);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--darkgray);
  background: var(--lightgray);
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 0.3rem 0.85rem;
  cursor: pointer;
  transition: background 0.12s;
}
#cdg-unit-toggle:hover { background: var(--secondary); color: #fff; }

.cdg-pair {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

.cdg-guess-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.cdg-input {
  flex: 1;
  font-family: var(--bodyFont);
  font-size: 1rem;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--lightgray);
  border-radius: 6px;
  background: var(--light);
  color: var(--dark);
  outline: none;
  transition: border-color 0.12s;
  -moz-appearance: textfield;
}
.cdg-input::-webkit-outer-spin-button,
.cdg-input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.cdg-input:focus { border-color: var(--secondary); }

.cdg-btn {
  font-family: var(--bodyFont);
  font-size: 0.88rem;
  font-weight: 600;
  color: #fff;
  background: var(--secondary);
  border: none;
  border-radius: 6px;
  padding: 0.55rem 1.2rem;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.12s;
}
.cdg-btn:hover { opacity: 0.85; }
.cdg-btn-wide { width: 100%; margin-top: 1.5rem; padding: 0.7rem; }

.cdg-reveal {
  animation: cdg-fadein 0.22s ease;
}
@keyframes cdg-fadein {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: translateY(0); }
}

.cdg-score-line {
  margin-bottom: 1.25rem;
}
.cdg-pts {
  font-size: 2rem;
  font-weight: 800;
}
.cdg-pts-label {
  font-size: 0.9rem;
  color: var(--gray);
}

.cdg-bar-wrap { margin-bottom: 1.5rem; display: flex; flex-direction: column; gap: 0.6rem; }

.cdg-bar-row {
  display: grid;
  grid-template-columns: 80px 1fr auto;
  align-items: center;
  gap: 0.6rem;
}

.cdg-bar-label {
  font-size: 0.75rem;
  color: var(--gray);
  text-align: right;
  white-space: nowrap;
}

.cdg-bar-track {
  height: 10px;
  background: var(--lightgray);
  border-radius: 5px;
  overflow: hidden;
}

.cdg-bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.cdg-bar-actual { background: var(--gray); }

.cdg-bar-val {
  font-size: 0.78rem;
  color: var(--darkgray);
  white-space: nowrap;
  min-width: 80px;
}

.cdg-next-wrap { text-align: right; }

.cdg-final {
  animation: cdg-fadein 0.3s ease;
  text-align: center;
}

.cdg-final-score {
  font-size: 3rem;
  font-weight: 800;
  color: var(--dark);
  line-height: 1;
  margin-bottom: 0.5rem;
}
.cdg-final-max { font-size: 1.4rem; color: var(--gray); font-weight: 500; }

.cdg-final-comment {
  font-size: 0.95rem;
  color: var(--gray);
  margin-bottom: 1.75rem;
}

.cdg-summary-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}
.cdg-summary-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--lightgray);
  color: var(--darkgray);
}
.cdg-summary-table tr:last-child td { border-bottom: none; }

@media (max-width: 480px) {
  .cdg-pair { font-size: 1.2rem; }
  .cdg-bar-row { grid-template-columns: 70px 1fr auto; }
}
</style>
