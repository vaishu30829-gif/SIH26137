const sourceInput = document.getElementById('source');
const destinationInput = document.getElementById('destination');
const scenarioInput = document.getElementById('scenario');
const runButton = document.getElementById('run');
const benchmarkButton = document.getElementById('benchmark');
const statusEl = document.getElementById('status');
const graphInfo = document.getElementById('graphInfo');
const scenarioBadge = document.getElementById('scenarioBadge');
const edgeInfo = document.getElementById('edgeInfo');
const resultBody = document.querySelector('#results tbody');
const recommended = document.getElementById('recommended');
const benchmarkBody = document.querySelector('#benchmark tbody');
const scenarioRoutes = document.getElementById('scenarioRoutes');

let map = null;
let roadLayers = [];
let routeLayer = null;
let markers = [];

function initMap() {
  map = L.map('map').setView([16.3, 80.45], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
}

function clearMap() {
  roadLayers.forEach(layer => layer.remove());
  roadLayers = [];
  if (routeLayer) { routeLayer.remove(); routeLayer = null; }
  markers.forEach(m => m.remove());
  markers = [];
}

function edgePopup(e) {
  const name = e.name ? `<br><b>Road:</b> ${escapeHtml(e.name)}` : '';
  return `<b>${e.source} → ${e.target}</b>${name}<br>` +
    `Distance: ${e.distance.toFixed(3)} km<br>` +
    `Speed: ${e.speed.toFixed(1)} km/h<br>` +
    `Capacity: ${e.capacity.toFixed(0)} veh/h<br>` +
    `Traffic: ${e.traffic.toFixed(0)} veh/h<br>` +
    `Travel time: ${(e.travel_time * 60).toFixed(2)} min<br>` +
    `Congestion: ${e.congestion.toFixed(2)}×<br>` +
    `Dynamic weight: ${e.weight.toFixed(3)}`;
}

function renderNetwork(data, bestPath = []) {
  if (!map) initMap();
  clearMap();
  const bestEdges = new Set(bestPath.slice(1).map((n, i) => `${bestPath[i]}|${n}`));
  const nodeMap = new Map(data.nodes.map(n => [String(n.id), n]));

  data.edges.forEach(e => {
    const geometry = e.geometry && e.geometry.length >= 2
      ? e.geometry
      : [[nodeMap.get(String(e.source)).y, nodeMap.get(String(e.source)).x], [nodeMap.get(String(e.target)).y, nodeMap.get(String(e.target)).x]];
    const layer = L.polyline(geometry, {
      color: bestEdges.has(`${e.source}|${e.target}`) ? '#087f5b' : '#64748b',
      weight: bestEdges.has(`${e.source}|${e.target}`) ? 6 : 2,
      opacity: bestEdges.has(`${e.source}|${e.target}`) ? 0.95 : 0.45
    }).addTo(map);
    layer.on('click', () => { edgeInfo.innerHTML = edgePopup(e); });
    layer.bindTooltip(`${e.name || 'Road'} · ${e.weight.toFixed(2)}`, {sticky: true});
    roadLayers.push(layer);
  });

  if (data.source) {
    const m = L.marker([data.source.lat, data.source.lon]).addTo(map).bindPopup(`<b>Source</b><br>${escapeHtml(data.source.display_name)}`);
    markers.push(m);
  }
  if (data.target) {
    const m = L.marker([data.target.lat, data.target.lon]).addTo(map).bindPopup(`<b>Destination</b><br>${escapeHtml(data.target.display_name)}`);
    markers.push(m);
  }
  if (data.source && data.target) {
    const bounds = L.latLngBounds([[data.source.lat, data.source.lon], [data.target.lat, data.target.lon]]);
    map.fitBounds(bounds.pad(0.35));
  }
}

function drawBestRoute(data, best) {
  if (!best || !data.nodes) return;
  const nodeMap = new Map(data.nodes.map(n => [String(n.id), n]));
  const coords = best.path.map(id => {
    const n = nodeMap.get(String(id));
    return n ? [n.y, n.x] : null;
  }).filter(Boolean);
  if (coords.length > 1) {
    routeLayer = L.polyline(coords, {color: '#d9480f', weight: 8, opacity: 0.9}).addTo(map);
    routeLayer.bringToFront();
  }
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

function renderResults(data) {
  const best = data.recommended;
  resultBody.innerHTML = '';
  Object.values(data.results).forEach(x => {
    const tr = document.createElement('tr');
    if (x.path.join(',') === best.path.join(',')) tr.classList.add('best');
    tr.innerHTML = `<td><b>${escapeHtml(x.algorithm)}</b></td>` +
      `<td>${escapeHtml(x.path.join(' → '))}</td>` +
      `<td>${x.distance.toFixed(3)}</td>` +
      `<td>${(x.travel_time * 60).toFixed(2)}</td>` +
      `<td>${x.congestion.toFixed(3)}</td>` +
      `<td>${x.fitness.toFixed(4)}</td>` +
      `<td>${(x.runtime * 1000).toFixed(2)}</td>`;
    resultBody.appendChild(tr);
  });
  recommended.innerHTML = `<b>Computed recommendation for ${escapeHtml(data.scenario)}</b><br>` +
    `<span class="path">${escapeHtml(best.path.join(' → '))}</span><br>` +
    `<span class="muted">Fitness ${best.fitness.toFixed(4)} · ${best.distance.toFixed(3)} km · ${(best.travel_time * 60).toFixed(2)} min · congestion ${best.congestion.toFixed(3)}</span>`;
  scenarioBadge.textContent = data.scenario.replace('_', ' ').toUpperCase();
  graphInfo.textContent = `${data.graph.nodes} nodes · ${data.graph.edges} directed road segments · ${data.graph.data_source}`;
}

async function runAll() {
  const source = sourceInput.value.trim();
  const destination = destinationInput.value.trim();
  if (!source || !destination) { alert('Enter both source and destination.'); return; }
  statusEl.textContent = 'Loading real road graph and running all six algorithms…';
  runButton.disabled = true;
  try {
    const response = await fetch('/api/real-route', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({source, destination, scenario: scenarioInput.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Routing failed');
    renderNetwork(data, data.recommended.path);
    renderResults(data);
    drawBestRoute(data, data.recommended);
    statusEl.textContent = 'Real-world route computed';
  } catch (err) {
    statusEl.textContent = 'Routing failed';
    alert(err.message);
  } finally { runButton.disabled = false; }
}

async function runBenchmark() {
  const source = sourceInput.value.trim();
  const destination = destinationInput.value.trim();
  if (!source || !destination) { alert('Enter both source and destination.'); return; }
  statusEl.textContent = 'Running 4 traffic scenarios × 6 algorithms × 3 trials…';
  benchmarkButton.disabled = true;
  try {
    const response = await fetch('/api/real-benchmark', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({source, destination, trials: 3, max_nodes: 220})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Benchmark failed');
    benchmarkBody.innerHTML = '';
    for (const scenario of ['free_flow','moderate','rush_hour','incident']) {
      for (const algorithm of ['Dijkstra','A*','ACO','PSO','QPSO','Quantum-QPSO']) {
        const x = data.aggregates[algorithm][scenario];
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${scenario.replace('_',' ')}</td><td><b>${algorithm}</b></td>` +
          `<td>${x.mean_fitness.toFixed(4)}</td><td>${x.mean_distance_km.toFixed(3)}</td>` +
          `<td>${(x.mean_travel_time_h * 60).toFixed(2)}</td><td>${x.mean_congestion.toFixed(3)}</td>` +
          `<td>${(x.mean_runtime_s * 1000).toFixed(2)}</td>`;
        benchmarkBody.appendChild(tr);
      }
    }
    scenarioRoutes.innerHTML = '<h3>Computed best route per traffic scenario</h3>';
    for (const scenario of ['free_flow','moderate','rush_hour','incident']) {
      const best = data.scenarios[scenario].recommended;
      scenarioRoutes.innerHTML += `<div class="scenario-row"><b>${scenario.replace('_',' ')}</b>: ${escapeHtml(best.algorithm)} → ${escapeHtml(best.path.join(' → '))} · fitness ${best.fitness.toFixed(4)}</div>`;
    }
    statusEl.textContent = `Benchmark complete — ${data.benchmark_file}`;
  } catch (err) {
    statusEl.textContent = 'Benchmark failed';
    alert(err.message);
  } finally { benchmarkButton.disabled = false; }
}

runButton.addEventListener('click', runAll);
benchmarkButton.addEventListener('click', runBenchmark);
initMap();
