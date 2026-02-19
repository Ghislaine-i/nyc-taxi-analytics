/**
 * NYC Taxi Trip Explorer — Dashboard JavaScript
 * Member C | Frontend logic: API calls, Chart.js charts, filters, table
 * Backend API: http://localhost:5000/api
 */

"use strict";

// ── CONFIGURATION ────────────────────────────────────────────────────
const API_BASE = "http://localhost:5000/api";

// Colour palette
const COLOR = {
  blue: "rgba(74, 140, 240, 0.85)",
  green: "rgba(39, 196, 122, 0.85)",
  yellow: "rgba(232, 184, 75, 0.85)",
  purple: "rgba(155, 125, 240, 0.85)",
  red: "rgba(233, 96, 96, 0.85)",
  orange: "rgba(251, 146, 60, 0.85)",
  teal: "rgba(45, 201, 168, 0.85)",
};

const BOROUGH_COLOR = {
  "Manhattan": COLOR.blue,
  "Brooklyn": COLOR.green,
  "Queens": COLOR.yellow,
  "Bronx": COLOR.red,
  "Staten Island": COLOR.purple,
  "EWR": COLOR.teal,
  "Unknown": "rgba(66, 77, 98, 0.6)",
};

// Chart.js global defaults — dark theme
Chart.defaults.color = "#7d8899";
Chart.defaults.borderColor = "#1d2438";
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.legend.labels.padding = 16;
Chart.defaults.plugins.tooltip.backgroundColor = "#161b26";
Chart.defaults.plugins.tooltip.borderColor = "#232d44";
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.titleColor = "#dde1eb";
Chart.defaults.plugins.tooltip.bodyColor = "#7d8899";

// Chart instance registry (so we can destroy before re-rendering)
const charts = {};

// Active filter state
let filters = {};
let locationMode = "pickup";


// ── UTILITIES ────────────────────────────────────────────────────────

async function fetchAPI(path) {
  try {
    const res = await fetch(API_BASE + path);
    if (!res.ok) throw new Error("HTTP " + res.status);
    return await res.json();
  } catch (err) {
    console.warn("API call failed:", path, err.message);
    return null;
  }
}

function fmtNumber(n) {
  if (n == null) return "--";
  return Number(n).toLocaleString();
}

function fmtDollar(n) {
  if (n == null) return "--";
  return "$" + Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtFixed(n, dp) {
  if (n == null) return "--";
  return Number(n).toFixed(dp);
}

function hourLabel(h) {
  const suffix = h < 12 ? "am" : "pm";
  const display = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return display + suffix;
}

function boroughClass(b) {
  if (!b) return "other";
  const s = b.toLowerCase();
  if (s === "manhattan") return "manhattan";
  if (s === "brooklyn") return "brooklyn";
  if (s === "queens") return "queens";
  if (s === "bronx") return "bronx";
  if (s === "staten island") return "staten";
  return "other";
}

function buildQueryString(extra) {
  const merged = Object.assign({}, filters, extra || {});
  const parts = [];
  for (const key in merged) {
    if (merged[key] !== "" && merged[key] != null) {
      parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(merged[key]));
    }
  }
  return parts.length ? "?" + parts.join("&") : "";
}

function destroyChart(key) {
  if (charts[key]) {
    charts[key].destroy();
    delete charts[key];
  }
}

function formatDatetime(dt) {
  if (!dt) return "--";
  try {
    return new Date(dt).toLocaleString("en-US", {
      month: "short", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  } catch (_) { return dt; }
}


// ── CONNECTION STATUS ────────────────────────────────────────────────

async function checkConnection() {
  const dot = document.getElementById("statusDot");
  const label = document.getElementById("connectionLabel");
  const result = await fetchAPI("/health");
  if (result && result.success) {
    dot.className = "status-dot connected";
    label.textContent = result.database === "connected" ? "API connected" : "API running (DB offline)";
  } else {
    dot.className = "status-dot disconnected";
    label.textContent = "API offline — displaying sample data";
  }
}


// ── KPI CARDS ────────────────────────────────────────────────────────

async function loadKPI() {
  const result = await fetchAPI("/stats/summary");
  if (!result || !result.success) {
    loadSampleKPI();
    return;
  }
  const d = result.data;
  document.getElementById("valTotalTrips").textContent = fmtNumber(d.total_trips);
  document.getElementById("valRevenue").textContent = fmtDollar(d.total_revenue);
  document.getElementById("valAvgFare").textContent = fmtDollar(d.avg_fare);
  document.getElementById("valAvgDist").textContent = fmtFixed(d.avg_distance, 2) + " mi";
  document.getElementById("valAvgSpeed").textContent = fmtFixed(d.avg_speed, 1) + " mph";
  document.getElementById("valAvgDuration").textContent = fmtFixed(d.avg_duration, 1) + " min";
}

function loadSampleKPI() {
  document.getElementById("valTotalTrips").textContent = "50,000";
  document.getElementById("valRevenue").textContent = "$768,412.30";
  document.getElementById("valAvgFare").textContent = "$15.37";
  document.getElementById("valAvgDist").textContent = "3.12 mi";
  document.getElementById("valAvgSpeed").textContent = "16.8 mph";
  document.getElementById("valAvgDuration").textContent = "14.6 min";
}


// ── CHART 1: HOURLY PATTERN (combo: bar + line) ──────────────────────

async function loadHourlyChart() {
  const result = await fetchAPI("/insights/hourly_pattern");
  destroyChart("hourly");
  const ctx = document.getElementById("chartHourly").getContext("2d");

  let labels, trips, speeds;

  if (result && result.success && result.data.length) {
    labels = result.data.map(function (d) { return hourLabel(d.hour); });
    trips = result.data.map(function (d) { return d.trip_count; });
    speeds = result.data.map(function (d) { return d.avg_speed; });
  } else {
    labels = [];
    for (var i = 0; i < 24; i++) labels.push(hourLabel(i));
    trips = [175, 118, 80, 68, 62, 93, 315, 675, 915, 835, 785, 805, 865, 808, 775, 828, 1048, 1235, 1095, 958, 818, 665, 488, 308];
    speeds = [22, 25, 28, 30, 29, 24, 18, 13, 12, 14, 15, 14, 13, 14, 14, 13, 12, 11, 12, 14, 16, 18, 20, 22];
  }

  charts.hourly = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Trip Count",
          data: trips,
          backgroundColor: COLOR.blue,
          borderRadius: 4,
          yAxisID: "yTrips",
          order: 2,
        },
        {
          label: "Avg Speed (mph)",
          data: speeds,
          type: "line",
          borderColor: COLOR.yellow,
          backgroundColor: "rgba(232,184,75,0.1)",
          pointBackgroundColor: COLOR.yellow,
          pointRadius: 3,
          tension: 0.4,
          fill: true,
          yAxisID: "ySpeed",
          order: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "top" } },
      scales: {
        yTrips: { position: "left", title: { display: true, text: "Trips" }, grid: { color: "#1d2438" } },
        ySpeed: { position: "right", title: { display: true, text: "Speed (mph)" }, grid: { drawOnChartArea: false } },
        x: { grid: { color: "#1d2438" } },
      },
    },
  });
}


// ── CHART 2: BOROUGH PIE ─────────────────────────────────────────────

async function loadBoroughPie() {
  const result = await fetchAPI("/insights/borough_stats");
  destroyChart("borough");
  const ctx = document.getElementById("chartBorough").getContext("2d");

  var labels, values, colours;

  if (result && result.success && result.data.length) {
    labels = result.data.map(function (d) { return d.borough || "Unknown"; });
    values = result.data.map(function (d) { return d.trip_count; });
    colours = labels.map(function (b) { return BOROUGH_COLOR[b] || BOROUGH_COLOR["Unknown"]; });
  } else {
    labels = ["Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island"];
    values = [33200, 9600, 5100, 1800, 600];
    colours = labels.map(function (b) { return BOROUGH_COLOR[b]; });
  }

  charts.borough = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: colours,
        borderColor: "#161b26",
        borderWidth: 3,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: function (ctx) { return " " + ctx.label + ": " + fmtNumber(ctx.parsed) + " trips"; }
          }
        }
      },
    },
  });
}


// ── CHART 3: FARE DISTRIBUTION ────────────────────────────────────────

async function loadFareDistChart() {
  const result = await fetchAPI("/insights/fare_distribution");
  destroyChart("fareDist");
  const ctx = document.getElementById("chartFareDist").getContext("2d");

  var labels, values;

  if (result && result.success && result.data.length) {
    labels = result.data.map(function (d) { return d.fare_range; });
    values = result.data.map(function (d) { return d.trip_count; });
  } else {
    labels = ["$0-10", "$10-20", "$20-30", "$30-50", "$50-100", "$100+"];
    values = [8100, 18600, 11500, 7500, 3400, 900];
  }

  charts.fareDist = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Number of Trips",
        data: values,
        backgroundColor: [COLOR.green, COLOR.blue, COLOR.yellow, COLOR.orange, COLOR.purple, COLOR.red],
        borderRadius: 5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#1d2438" } },
        y: { grid: { color: "#1d2438" }, title: { display: true, text: "Trips" } },
      },
    },
  });
}


// ── CHART 4: DISTANCE DISTRIBUTION ───────────────────────────────────

async function loadDistDistChart() {
  const result = await fetchAPI("/insights/distance_distribution");
  destroyChart("distDist");
  const ctx = document.getElementById("chartDistDist").getContext("2d");

  var labels, values;

  if (result && result.success && result.data.length) {
    labels = result.data.map(function (d) { return d.distance_range; });
    values = result.data.map(function (d) { return d.trip_count; });
  } else {
    labels = ["< 1 mile", "1-3 miles", "3-5 miles", "5-10 miles", "10+ miles"];
    values = [5900, 21200, 12400, 7300, 3200];
  }

  charts.distDist = new Chart(ctx, {
    type: "polarArea",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: [COLOR.teal, COLOR.blue, COLOR.green, COLOR.yellow, COLOR.orange],
        borderColor: "#161b26",
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { r: { grid: { color: "#1d2438" }, ticks: { display: false } } },
    },
  });
}


// ── CHART 5: DAY OF WEEK ─────────────────────────────────────────────

async function loadDayOfWeekChart() {
  const result = await fetchAPI("/insights/day_of_week");
  destroyChart("dayOfWeek");
  const ctx = document.getElementById("chartDayOfWeek").getContext("2d");

  var labels, trips, fares;

  if (result && result.success && result.data.length) {
    var sorted = result.data.slice().sort(function (a, b) { return a.day_number - b.day_number; });
    labels = sorted.map(function (d) { return (d.day_name || "").trim().slice(0, 3); });
    trips = sorted.map(function (d) { return d.trip_count; });
    fares = sorted.map(function (d) { return d.avg_fare; });
  } else {
    labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    trips = [6100, 7750, 7480, 7900, 8100, 8850, 7620];
    fares = [15.2, 14.8, 14.6, 15.1, 15.4, 16.1, 16.7];
  }

  charts.dayOfWeek = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Trip Count (x100)",
          data: trips.map(function (v) { return Math.round(v / 100); }),
          borderColor: COLOR.blue,
          backgroundColor: "rgba(74,140,240,0.12)",
          pointBackgroundColor: COLOR.blue,
          pointRadius: 4,
        },
        {
          label: "Avg Fare ($)",
          data: fares,
          borderColor: COLOR.yellow,
          backgroundColor: "rgba(232,184,75,0.08)",
          pointBackgroundColor: COLOR.yellow,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          grid: { color: "#1d2438" },
          angleLines: { color: "#1d2438" },
          pointLabels: { font: { size: 11 } },
        },
      },
      plugins: { legend: { position: "bottom" } },
    },
  });
}


// ── CHART 6: TOP LOCATIONS ────────────────────────────────────────────

async function loadTopLocationsChart(mode) {
  locationMode = mode || "pickup";
  const result = await fetchAPI("/insights/top_locations?limit=10&type=" + locationMode);
  destroyChart("topLocations");
  const ctx = document.getElementById("chartTopLocations").getContext("2d");

  var labels, values, colours;

  if (result && result.success && result.data.length) {
    var data = result.data.slice(0, 10);
    labels = data.map(function (d) { return d.zone || "Unknown"; });
    values = data.map(function (d) { return d.trip_count; });
    colours = data.map(function (d) { return BOROUGH_COLOR[d.borough] || BOROUGH_COLOR["Unknown"]; });
  } else {
    labels = ["JFK Airport", "Times Sq/Theatre District", "Penn Station/Madison Sq W", "Midtown Center",
      "Upper East Side N", "Lincoln Square E", "East Village", "Lenox Hill W",
      "Hell's Kitchen N", "Williamsburg (N Side)"];
    values = [3240, 2980, 2650, 2430, 2280, 2010, 1880, 1740, 1620, 1480];
    colours = new Array(10).fill(COLOR.blue);
  }

  charts.topLocations = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Trips",
        data: values,
        backgroundColor: colours,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#1d2438" }, title: { display: true, text: "Number of Trips" } },
        y: { grid: { display: false } },
      },
    },
  });
}

function switchLocation(mode) {
  document.getElementById("btnPickup").classList.toggle("active", mode === "pickup");
  document.getElementById("btnDropoff").classList.toggle("active", mode === "dropoff");
  loadTopLocationsChart(mode);
}


// ── CHART 7: BOROUGH COMPARISON ───────────────────────────────────────

async function loadBoroughCompareChart() {
  const result = await fetchAPI("/insights/borough_stats");
  destroyChart("boroughCompare");
  const ctx = document.getElementById("chartBoroughCompare").getContext("2d");

  var labels, fares, distances, speeds;

  if (result && result.success && result.data.length) {
    var data = result.data.filter(function (d) { return !!d.borough; });
    labels = data.map(function (d) { return d.borough; });
    fares = data.map(function (d) { return d.avg_fare; });
    distances = data.map(function (d) { return d.avg_distance; });
    speeds = data.map(function (d) { return d.avg_speed; });
  } else {
    labels = ["Manhattan", "Queens", "Brooklyn", "Bronx", "Staten Island"];
    fares = [14.8, 19.1, 12.4, 11.6, 17.3];
    distances = [2.8, 4.1, 2.3, 2.7, 5.2];
    speeds = [14.2, 20.1, 16.8, 17.9, 22.4];
  }

  charts.boroughCompare = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Avg Fare ($)",
          data: fares,
          backgroundColor: COLOR.yellow,
          borderRadius: 4,
          yAxisID: "yFare",
        },
        {
          label: "Avg Distance (mi)",
          data: distances,
          backgroundColor: COLOR.blue,
          borderRadius: 4,
          yAxisID: "yDist",
        },
        {
          label: "Avg Speed (mph)",
          data: speeds,
          type: "line",
          borderColor: COLOR.green,
          backgroundColor: "transparent",
          pointBackgroundColor: COLOR.green,
          pointRadius: 5,
          tension: 0.3,
          yAxisID: "ySpeed",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "top" } },
      scales: {
        yFare: { position: "left", title: { display: true, text: "Fare ($)" }, grid: { color: "#1d2438" } },
        yDist: { position: "right", title: { display: true, text: "Distance (mi)" }, grid: { drawOnChartArea: false } },
        ySpeed: { position: "right", title: { display: true, text: "Speed (mph)" }, grid: { drawOnChartArea: false }, offset: true },
        x: { grid: { color: "#1d2438" } },
      },
    },
  });
}


// ── DATA TABLE ────────────────────────────────────────────────────────

async function loadTripsTable() {
  var limit = document.getElementById("tableLimit").value;
  var tbody = document.getElementById("tableBody");
  var footer = document.getElementById("tableFooter");

  tbody.innerHTML = '<tr><td colspan="12" class="table-placeholder">Loading records...</td></tr>';

  var qs = buildQueryString({ limit: limit });
  var result = await fetchAPI("/trips" + qs);

  if (!result || !result.success || !result.data.length) {
    tbody.innerHTML = '<tr><td colspan="12" class="table-placeholder">No data returned. Check that the backend is running.</td></tr>';
    footer.textContent = "0 records";
    return;
  }

  var rows = result.data;
  tbody.innerHTML = rows.map(function (r) {
    var bc = boroughClass(r.pickup_borough);
    return "<tr>" +
      "<td>" + formatDatetime(r.tpep_pickup_datetime) + "</td>" +
      "<td>" + formatDatetime(r.tpep_dropoff_datetime) + "</td>" +
      "<td>" + (r.pickup_zone || "--") + "</td>" +
      "<td>" + (r.dropoff_zone || "--") + "</td>" +
      "<td><span class='badge badge-" + bc + "'>" + (r.pickup_borough || "--") + "</span></td>" +
      "<td>" + fmtFixed(r.trip_distance, 2) + "</td>" +
      "<td>" + fmtFixed(r.trip_duration_minutes, 1) + "</td>" +
      "<td>" + fmtDollar(r.fare_amount) + "</td>" +
      "<td>" + fmtDollar(r.tip_amount) + "</td>" +
      "<td>" + fmtDollar(r.total_amount) + "</td>" +
      "<td>" + fmtFixed(r.avg_speed_mph, 1) + "</td>" +
      "<td>" + (r.passenger_count != null ? r.passenger_count : "--") + "</td>" +
      "</tr>";
  }).join("");

  footer.textContent = "Showing " + rows.length + " of " + fmtNumber(result.count) + " records";
}


// ── FILTERS ───────────────────────────────────────────────────────────

function applyFilters() {
  filters = {};
  var borough = document.getElementById("filterBorough").value;
  var minFare = document.getElementById("filterMinFare").value;
  var maxFare = document.getElementById("filterMaxFare").value;
  var date = document.getElementById("filterDate").value;

  if (borough) filters.borough = borough;
  if (minFare) filters.min_fare = minFare;
  if (maxFare) filters.max_fare = maxFare;
  if (date) filters.date = date;

  loadTripsTable();
}

function resetFilters() {
  document.getElementById("filterBorough").value = "";
  document.getElementById("filterMinFare").value = "";
  document.getElementById("filterMaxFare").value = "";
  document.getElementById("filterDate").value = "";
  filters = {};
  loadTripsTable();
  loadKPI();
}


// ── INIT ──────────────────────────────────────────────────────────────

async function initDashboard() {
  await checkConnection();

  // Load all sections in parallel
  await Promise.all([
    loadKPI(),
    loadHourlyChart(),
    loadBoroughPie(),
    loadFareDistChart(),
    loadDistDistChart(),
    loadDayOfWeekChart(),
    loadTopLocationsChart("pickup"),
    loadBoroughCompareChart(),
    loadTripsTable(),
  ]);
}

document.addEventListener("DOMContentLoaded", initDashboard);
