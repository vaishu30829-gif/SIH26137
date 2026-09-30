import heapq
import math


def _validate(network, source, target, weight):
    if source not in network.nodes:
        raise ValueError(f"Unknown source node: {source}")
    if target not in network.nodes:
        raise ValueError(f"Unknown target node: {target}")
    if weight == "dynamic":
        weight = "weight"
    if weight not in {"distance", "travel_time", "congestion", "weight"}:
        raise ValueError("Unsupported weight")
    return weight


def shortest_path(network, source, target, weight="distance"):
    weight = _validate(network, source, target, weight)
    distances = {node: float("inf") for node in network.nodes}
    previous = {node: None for node in network.nodes}
    distances[source] = 0.0
    queue = [(0.0, source)]

    while queue:
        cost, node = heapq.heappop(queue)
        if cost > distances[node]:
            continue
        if node == target:
            break
        for neighbor in network.get_neighbors(node):
            edge_cost = network.edge_weight(node, neighbor, weight)
            new_cost = cost + edge_cost
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = node
                heapq.heappush(queue, (new_cost, neighbor))

    if distances[target] == float("inf"):
        return None, float("inf")
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path, distances[target]


def a_star(network, source, target, weight="weight"):
    weight = _validate(network, source, target, weight)

    def heuristic(node):
        a = network.nodes[node]
        b = network.nodes[target]
        euclidean = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
        if weight == "distance":
            return euclidean
        # Conservative lower bound for time/dynamic weight.
        max_speed = max(data["speed"] for data in network.edges.values())
        if weight == "travel_time":
            return euclidean / max_speed
        if weight == "weight":
            return euclidean  # non-negative lower bound
        return 0.0

    g = {node: float("inf") for node in network.nodes}
    previous = {node: None for node in network.nodes}
    g[source] = 0.0
    queue = [(heuristic(source), 0.0, source)]

    while queue:
        _, current_g, node = heapq.heappop(queue)
        if current_g > g[node]:
            continue
        if node == target:
            break
        for neighbor in network.get_neighbors(node):
            edge_cost = network.edge_weight(node, neighbor, weight)
            new_g = current_g + edge_cost
            if new_g < g[neighbor]:
                g[neighbor] = new_g
                previous[neighbor] = node
                heapq.heappush(queue, (new_g + heuristic(neighbor), new_g, neighbor))

    if g[target] == float("inf"):
        return None, float("inf")
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = previous[node]
    path.reverse()
    return path, g[target]
