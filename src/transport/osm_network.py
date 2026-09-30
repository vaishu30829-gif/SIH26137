"""Real-world OpenStreetMap road graph loader for QRoute."""

from __future__ import annotations

import math
from collections import defaultdict
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

import networkx as nx

from src.transport.graph import RoadNetwork


def geocode_location(query: str) -> dict:
    """Geocode a human-entered location with OpenStreetMap Nominatim."""
    query = (query or "").strip()
    if not query:
        raise ValueError("Location cannot be empty.")
    params = urlencode({"q": query, "format": "jsonv2", "limit": 1})
    req = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "QRoute-SIH26137/1.0 (educational research project)"},
    )
    with urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not data:
        raise ValueError(f"Location not found: {query}")
    item = data[0]
    return {
        "query": query,
        "display_name": item.get("display_name", query),
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
    }


def _speed_kph(value, highway):
    if isinstance(value, list):
        value = value[0] if value else None
    try:
        if value is not None:
            text = str(value).lower().replace(" km/h", "").strip()
            return max(10.0, float(text))
    except ValueError:
        pass
    defaults = {
        "motorway": 90, "trunk": 70, "primary": 55, "secondary": 45,
        "tertiary": 35, "residential": 30, "unclassified": 30,
        "service": 20, "living_street": 15,
    }
    if isinstance(highway, list):
        highway = highway[0] if highway else "residential"
    return float(defaults.get(highway, 30))


def _capacity_veh_per_hour(data):
    lanes = data.get("lanes", 1)
    if isinstance(lanes, list):
        lanes = lanes[0] if lanes else 1
    try:
        lanes = max(1, int(float(str(lanes).split(";")[0])))
    except ValueError:
        lanes = 1
    highway = data.get("highway", "residential")
    if isinstance(highway, list):
        highway = highway[0] if highway else "residential"
    per_lane = {
        "motorway": 1800, "trunk": 1500, "primary": 1200,
        "secondary": 900, "tertiary": 700, "residential": 500,
        "unclassified": 450, "service": 300, "living_street": 250,
    }.get(highway, 500)
    return float(per_lane * lanes)


def _geometry_for_edge(data, source_data, target_data):
    geometry = data.get("geometry")
    if geometry is not None and hasattr(geometry, "coords"):
        return [[float(y), float(x)] for x, y in geometry.coords]
    return [
        [float(source_data["y"]), float(source_data["x"])],
        [float(target_data["y"]), float(target_data["x"])],
    ]


def _build_road_network(graph):
    network = RoadNetwork()
    for node, data in graph.nodes(data=True):
        network.add_node(node, data["x"], data["y"])

    # OSMnx MultiDiGraph can contain parallel edges. Keep the lowest-free-flow edge
    # between two nodes so the rest of QRoute can use a simple directed graph.
    chosen = {}
    for u, v, data in graph.edges(data=True):
        distance_m = float(data.get("length", 1.0))
        highway = data.get("highway", "residential")
        speed = _speed_kph(data.get("maxspeed") or data.get("speed_kph"), highway)
        key = (u, v)
        if key not in chosen or distance_m < chosen[key][0]:
            chosen[key] = (distance_m, speed, _capacity_veh_per_hour(data), data)

    for (u, v), (distance_m, speed, capacity, data) in chosen.items():
        network.add_edge(
            u,
            v,
            distance_m / 1000.0,
            speed,
            capacity,
            geometry=_geometry_for_edge(data, graph.nodes[u], graph.nodes[v]),
            name=data.get("name", "") if isinstance(data.get("name", ""), str) else str(data.get("name", "")),
        )
    return network


def _corridor_subgraph(graph, source_node, target_node, max_nodes):
    if len(graph.nodes) <= max_nodes:
        return graph
    try:
        backbone = nx.shortest_path(graph, source_node, target_node, weight="length")
    except nx.NetworkXNoPath:
        return graph.subgraph(list(graph.nodes)[:max_nodes]).copy()

    selected = set(backbone)
    # Expand around the backbone to preserve multiple real alternatives.
    for radius in (2, 3, 4):
        for node in list(selected):
            selected.update(nx.single_source_shortest_path_length(graph, node, cutoff=radius).keys())
        if len(selected) >= max_nodes:
            break

    if len(selected) > max_nodes:
        # Keep the backbone and the nearest nodes to it until the cap is reached.
        distances = nx.multi_source_dijkstra_path_length(graph, backbone, weight="length")
        ranked = sorted((n for n in selected if n not in backbone), key=lambda n: distances.get(n, float("inf")))
        selected = set(backbone) | set(ranked[: max(0, max_nodes - len(backbone))])
    return graph.subgraph(selected).copy()


def load_real_world_network(source, target, radius_m=3500, max_nodes=220):
    """Download a real OSM driving graph around the requested source/destination."""
    import osmnx as ox

    source_lat, source_lon = float(source["lat"]), float(source["lon"])
    target_lat, target_lon = float(target["lat"]), float(target["lon"])
    center = ((source_lat + target_lat) / 2.0, (source_lon + target_lon) / 2.0)

    # Ensure the requested endpoints are covered even when they are not close together.
    separation_m = math.hypot((source_lat - target_lat) * 111_000, (source_lon - target_lon) * 111_000 * math.cos(math.radians(center[0])))
    dist = max(float(radius_m), separation_m / 2.0 + 1200.0)
    dist = min(dist, 7000.0)

    graph = ox.graph.graph_from_point(
        center,
        dist=dist,
        dist_type="bbox",
        network_type="drive",
        simplify=True,
        retain_all=False,
    )

    source_node = ox.distance.nearest_nodes(graph, X=source_lon, Y=source_lat)
    target_node = ox.distance.nearest_nodes(graph, X=target_lon, Y=target_lat)
    graph = _corridor_subgraph(graph, source_node, target_node, max_nodes)

    if source_node not in graph.nodes or target_node not in graph.nodes:
        raise ValueError("The downloaded road graph did not retain both endpoints. Increase radius_m or max_nodes.")

    network = _build_road_network(graph)
    return network, source_node, target_node, {
        "source": source,
        "target": target,
        "nodes": len(network.nodes),
        "edges": len(network.edges),
        "radius_m": dist,
        "data_source": "OpenStreetMap via OSMnx/Overpass",
    }


def apply_traffic_scenario(network, scenario, seed=42):
    """Apply deterministic traffic demand to every real road edge."""
    import random

    rng = random.Random(seed)
    configs = {
        "free_flow": (0.20, 0.08, 0.00),
        "moderate": (0.55, 0.15, 0.00),
        "rush_hour": (0.85, 0.18, 0.00),
        "incident": (0.65, 0.12, 0.10),
    }
    if scenario not in configs:
        raise ValueError(f"Unknown traffic scenario: {scenario}")
    base, variation, incident_rate = configs[scenario]

    for (u, v), edge in network.edges.items():
        factor = max(0.02, base + rng.uniform(-variation, variation))
        if scenario == "incident" and rng.random() < incident_rate:
            factor *= rng.uniform(1.7, 2.8)
        network.update_traffic(u, v, factor * edge["capacity"])


def reset_traffic(network):
    for (u, v), edge in network.edges.items():
        network.update_traffic(u, v, 0.0)
