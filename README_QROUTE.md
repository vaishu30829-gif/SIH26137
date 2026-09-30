# QRoute - separated VRP and traffic-aware pathfinding

## Architecture

- **Traffic engine:** simulator now starts with non-zero traffic and updates BPR travel times.
- **Pathfinding:** Dijkstra, A*, ACO, PSO, QPSO and Quantum-QPSO all solve the same source-to-target weighted graph problem.
- **Recommended route:** all six results are compared using the same dynamic route fitness; the lowest-fitness result is highlighted on the graph.
- **VRP:** remains a separate layer. A VRP optimizer decides customer order/vehicle assignment. Physical road legs can then be evaluated by the routing layer.
- **Live traffic:** `LiveTrafficProvider.apply_snapshot()` accepts provider-normalized traffic data. Real API credentials/provider mapping must be supplied by the deployment.

## Run pathfinding demo

```powershell
python -m src.routing.demo_pathfinding
```

## Run web prototype

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

The browser provides one **RUN ALL PATHFINDERS** action. It does not ask the user to select an algorithm.

## Real-World Routing Mode

The web application now uses a real OpenStreetMap driving graph after the user enters a source and destination.

### Workflow

1. Enter a source location and destination location as normal text.
2. QRoute geocodes both locations through OpenStreetMap Nominatim.
3. QRoute downloads the surrounding driving road network through OSMnx/Overpass.
4. The graph is reduced to a bounded source-to-destination corridor so stochastic algorithms remain responsive.
5. The same weighted graph and traffic state are passed to all six algorithms:
   - Dijkstra
   - A*
   - ACO
   - PSO
   - QPSO
   - Quantum-QPSO
6. Traffic is represented by four executable scenarios:
   - Free flow
   - Moderate traffic
   - Rush hour
   - Incident/heavy congestion
7. The recommended route is the route with the lowest computed objective fitness for the selected scenario.
8. The benchmark executes all six algorithms across all four traffic scenarios and writes `results/real_world_benchmark.csv`.

### Objective

For a route P:

`F(P) = distance(P) + 10 * travel_time(P) + 2 * congestion(P)`

Every algorithm receives the same objective and current edge weights. Edge travel time uses a BPR-style congestion function:

`T = T0 * (1 + 0.15 * (traffic / capacity)^4)`

This makes a route change when traffic makes an alternative road cheaper.

### Installation

Use the existing Python 3.12 environment:

```powershell
cd C:\Users\Vyshu\QPSO-Qiskit
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

The first real-world query requires internet access because the application contacts OpenStreetMap/Nominatim and the OSM Overpass infrastructure. No Google Maps API key is required.

### Benchmark

The UI benchmark uses the same user-entered source and destination and runs:

`4 traffic scenarios × 6 algorithms × 3 trials`

The CSV contains fitness, distance, travel time, congestion, runtime, scenario, trial, algorithm, and the actual computed route.

Real-world road data is from OpenStreetMap. Traffic scenarios are simulated unless a separate live traffic provider is integrated; the application does not claim that the simulated traffic values are live measurements.
