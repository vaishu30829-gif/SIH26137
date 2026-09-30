from flask import Flask, jsonify, render_template, request

from src.transport.osm_network import (
    apply_traffic_scenario,
    geocode_location,
    load_real_world_network,
)
from src.routing.pathfinder_manager import PathfinderManager
from src.experiments.real_world_benchmark import benchmark_real_world, SCENARIOS

app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

# The graph is loaded from OpenStreetMap only after the user supplies source/destination.
state = {
    "network": None,
    "source": None,
    "target": None,
    "source_node": None,
    "target_node": None,
    "graph_info": None,
    "scenario": "moderate",
}


def network_payload():
    network = state["network"]
    if network is None:
        return {"nodes": [], "edges": []}
    nodes = [{"id": n, **data} for n, data in network.nodes.items()]
    edges = []
    for (source, target), data in network.edges.items():
        edges.append({"source": source, "target": target, **data})
    return {"nodes": nodes, "edges": edges}


def ensure_graph(source_query, target_query, radius_m=3500, max_nodes=220):
    source = geocode_location(source_query)
    target = geocode_location(target_query)
    network, source_node, target_node, info = load_real_world_network(
        source, target, radius_m=radius_m, max_nodes=max_nodes
    )
    state.update({
        "network": network,
        "source": source,
        "target": target,
        "source_node": source_node,
        "target_node": target_node,
        "graph_info": info,
    })
    return network


@app.get("/")
def index():
    return render_template("index.html", scenarios=SCENARIOS)


@app.get("/api/network")
def api_network():
    payload = network_payload()
    payload.update({
        "traffic_mode": "SIMULATED",
        "scenario": state["scenario"],
        "source": state["source"],
        "target": state["target"],
        "source_node": state["source_node"],
        "target_node": state["target_node"],
        "graph": state["graph_info"],
    })
    return jsonify(payload)


@app.post("/api/real-route")
def api_real_route():
    payload = request.get_json(silent=True) or {}
    source_query = str(payload.get("source", "")).strip()
    target_query = str(payload.get("destination", "")).strip()
    scenario = payload.get("scenario", "moderate")
    if not source_query or not target_query:
        return jsonify({"error": "Source and destination are required."}), 400
    if scenario not in SCENARIOS:
        return jsonify({"error": f"Unknown traffic scenario: {scenario}"}), 400

    try:
        network = ensure_graph(source_query, target_query)
        state["scenario"] = scenario
        apply_traffic_scenario(network, scenario, seed=42)
        manager = PathfinderManager(particles=10, iterations=15, seed=42)
        results = manager.find_all(network, state["source_node"], state["target_node"])
        best = manager.select_best(results)
        response = network_payload()
        response.update({
            "results": results,
            "recommended": best,
            "scenario": scenario,
            "source": state["source"],
            "target": state["target"],
            "source_node": state["source_node"],
            "target_node": state["target_node"],
            "graph": state["graph_info"],
        })
        return jsonify(response)
    except Exception as exc:
        app.logger.exception("Real-world routing failed")
        return jsonify({"error": str(exc)}), 500


@app.post("/api/real-benchmark")
def api_real_benchmark():
    payload = request.get_json(silent=True) or {}
    source_query = str(payload.get("source", "")).strip()
    target_query = str(payload.get("destination", "")).strip()
    if not source_query or not target_query:
        return jsonify({"error": "Source and destination are required."}), 400
    try:
        data = benchmark_real_world(
            source_query,
            target_query,
            radius_m=int(payload.get("radius_m", 3500)),
            max_nodes=int(payload.get("max_nodes", 220)),
            trials=int(payload.get("trials", 3)),
        )
        # Keep the last benchmark graph available for inspection in the UI.
        state.update({
            "network": None,
            "source": data["source"],
            "target": data["target"],
            "source_node": data["source_node"],
            "target_node": data["target_node"],
            "graph_info": data["graph"],
        })
        return jsonify(data)
    except Exception as exc:
        app.logger.exception("Benchmark failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
