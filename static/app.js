/**
 * app.js — Experiment 6 & 9: JavaScript Dynamic Pages + AJAX with JSON/XML
 * Polls the Flask API every 3 seconds and updates the dashboard in real time.
 */

'use strict';

// ── Configuration ──────────────────────────────────────────────────────────
const POLL_INTERVAL_MS = 3000;
const HISTORY_LIMIT    = 30;   // number of points on chart

let dataSource    = 'json';    // 'json' | 'xml'
let chartInstance = null;
let chartLabels   = [];
let chartTemp     = [];
let chartHum      = [];
let chartPres     = [];        // scaled for readability

const WIND_DEGREES = { N:0, NE:45, E:90, SE:135, S:180, SW:225, W:270, NW:315 };

// ── Helpers ────────────────────────────────────────────────────────────────

function el(id) { return document.getElementById(id); }

function setSource(src) {
  dataSource = src;
  el('btn-json').classList.toggle('active', src === 'json');
  el('btn-xml').classList.toggle('active',  src === 'xml');
  el('raw-format-label').textContent = src.toUpperCase();
}

function dismissAlert() {
  el('alert-banner').classList.add('hidden');
}

function formatTime(dtStr) {
  if (!dtStr) return '—';
  const d = new Date(dtStr.replace(' ', 'T') + 'Z');
  return d.toLocaleTimeString();
}

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

// ── Chart Initialisation ───────────────────────────────────────────────────

function initChart() {
  const ctx = el('main-chart').getContext('2d');
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartLabels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: chartTemp,
          borderColor: '#00d4ff', backgroundColor: 'rgba(0,212,255,0.07)',
          borderWidth: 2, pointRadius: 2, tension: 0.4, fill: true,
        },
        {
          label: 'Humidity (%)',
          data: chartHum,
          borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.07)',
          borderWidth: 2, pointRadius: 2, tension: 0.4, fill: true,
        },
        {
          label: 'Pressure (scaled)',
          data: chartPres,
          borderColor: '#34d399', backgroundColor: 'rgba(52,211,153,0.07)',
          borderWidth: 2, pointRadius: 2, tension: 0.4, fill: true,
        }
      ]
    },
    options: {
      responsive: true,
      animation: { duration: 400 },
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(13,21,38,0.95)',
          borderColor: 'rgba(0,212,255,0.2)',
          borderWidth: 1,
          titleColor: '#00d4ff',
          bodyColor: '#c0c0d0',
        }
      },
      scales: {
        x: {
          ticks: { color: '#4a5568', maxTicksLimit: 8, font: { size: 10 } },
          grid:  { color: 'rgba(255,255,255,0.04)' }
        },
        y: {
          ticks: { color: '#4a5568', font: { size: 10 } },
          grid:  { color: 'rgba(255,255,255,0.04)' }
        }
      }
    }
  });
}

// ── Update UI ─────────────────────────────────────────────────────────────

function updateCards(d) {
  if (!d || !d.temperature) return;

  // Values
  el('val-temp').textContent  = parseFloat(d.temperature).toFixed(1);
  el('val-hum').textContent   = parseFloat(d.humidity).toFixed(1);
  el('val-pres').textContent  = parseFloat(d.pressure).toFixed(1);
  el('val-wind').textContent  = parseFloat(d.wind_speed).toFixed(1);

  // Progress bars
  el('bar-temp').style.width  = clamp(((d.temperature + 10) / 60) * 100, 0, 100) + '%';
  el('bar-hum').style.width   = clamp(d.humidity, 0, 100) + '%';
  el('bar-pres').style.width  = clamp(((d.pressure - 950) / 100) * 100, 0, 100) + '%';
  el('bar-wind').style.width  = clamp((d.wind_speed / 120) * 100, 0, 100) + '%';

  // Station info
  if (d.station_name) el('station-name').textContent = d.station_name;
  if (d.location)     el('station-location').textContent = d.location;
  el('last-updated').textContent = formatTime(d.recorded_at);

  // Compass needle
  const dir    = (d.wind_direction || 'N').trim().toUpperCase();
  const deg    = WIND_DEGREES[dir] ?? 0;
  const needle = el('compass-needle');
  needle.style.transform = `translate(-50%, -100%) rotate(${deg}deg)`;
  el('compass-dir').textContent = dir;

  // Alert banner for extreme temperature
  const alertBanner = el('alert-banner');
  if (d.temperature > 42) {
    el('alert-text').textContent =
      `⚠ High Temperature Alert: ${parseFloat(d.temperature).toFixed(1)}°C at ${d.station_name || 'station'} — exceeds safe threshold!`;
    alertBanner.classList.remove('hidden');
  } else if (d.temperature < 5) {
    el('alert-text').textContent =
      `❄ Low Temperature Alert: ${parseFloat(d.temperature).toFixed(1)}°C — below minimum threshold!`;
    alertBanner.classList.remove('hidden');
  }
}

function updateChart(d) {
  if (!d || !d.temperature) return;
  const label = formatTime(d.recorded_at) || new Date().toLocaleTimeString();
  chartLabels.push(label);
  chartTemp.push(parseFloat(d.temperature).toFixed(2));
  chartHum.push(parseFloat(d.humidity).toFixed(2));
  chartPres.push(((parseFloat(d.pressure) - 1000) * 0.5).toFixed(2)); // scale near 0

  if (chartLabels.length > HISTORY_LIMIT) {
    chartLabels.shift(); chartTemp.shift(); chartHum.shift(); chartPres.shift();
  }
  chartInstance.update();
}

// ── Alerts List ────────────────────────────────────────────────────────────

async function fetchAlerts() {
  try {
    const resp = await fetch('/api/alerts');
    const data = await resp.json();
    const list = el('alerts-list');
    if (!data.alerts || data.alerts.length === 0) {
      list.innerHTML = '<li class="alert-item no-alerts">No alerts — conditions normal ✓</li>';
      return;
    }
    list.innerHTML = data.alerts.slice(0, 5).map(a =>
      `<li class="alert-item">
        <strong>${a.alert_type}</strong> — ${a.message}
        <br/><small style="opacity:0.6">${formatTime(a.triggered_at)}</small>
      </li>`
    ).join('');
  } catch (_) {}
}

// ── JSON Fetch ─────────────────────────────────────────────────────────────

async function fetchJSON() {
  const resp = await fetch('/api/current');
  if (!resp.ok) throw new Error('JSON fetch failed');
  const data = await resp.json();

  // Raw display
  el('raw-data').textContent = JSON.stringify(data, null, 2);
  return data;
}

// ── XML Fetch + Parse ──────────────────────────────────────────────────────

async function fetchXML() {
  const resp = await fetch('/api/readings.xml?limit=1');
  if (!resp.ok) throw new Error('XML fetch failed');
  const text = await resp.text();

  // Raw display
  el('raw-data').textContent = text.slice(0, 800);

  // Parse XML to get latest reading
  const parser  = new DOMParser();
  const xmlDoc  = parser.parseFromString(text, 'application/xml');
  const reading = xmlDoc.querySelector('Reading');
  if (!reading) return null;

  const get = tag => {
    const node = reading.querySelector(tag);
    return node ? node.textContent : null;
  };

  return {
    temperature:    get('temperature'),
    humidity:       get('humidity'),
    pressure:       get('pressure'),
    wind_speed:     get('wind_speed'),
    wind_direction: get('wind_direction'),
    recorded_at:    get('recorded_at'),
    station_name:   get('station_name'),
    location:       get('location'),
  };
}

// ── Main Poll Loop ─────────────────────────────────────────────────────────

async function poll() {
  try {
    const data = dataSource === 'xml' ? await fetchXML() : await fetchJSON();
    if (data) {
      updateCards(data);
      updateChart(data);
    }
    await fetchAlerts();
    el('live-badge').style.opacity = '1';
  } catch (err) {
    console.warn('[AJAX] Poll error:', err.message);
    el('live-badge').style.opacity = '0.3';
  }
}

// ── Initialise ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initChart();
  poll();
  setInterval(poll, POLL_INTERVAL_MS);
});
