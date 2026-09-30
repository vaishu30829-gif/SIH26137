class RoadNetwork:
    """Weighted directed transportation graph with traffic-aware edge weights."""

    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node_id, x, y):
        self.nodes[node_id] = {"x": float(x), "y": float(y)}

    def add_edge(self, source, target, distance, speed, capacity, geometry=None, name=None):
        if speed <= 0 or capacity <= 0:
            raise ValueError("speed and capacity must be positive")
        free_flow_time = distance / speed
        self.edges[(source, target)] = {
            "distance": float(distance),
            "speed": float(speed),
            "capacity": float(capacity),
            "free_flow_time": float(free_flow_time),
            "traffic": 0.0,
            "travel_time": float(free_flow_time),
            "congestion": 0.0,
            "weight": float(distance),
            "blocked": False,
            "geometry": geometry or [],
            "name": name or "",
        }
        self._recalculate_edge(source, target)

    def _recalculate_edge(self, source, target):
        edge = self.edges[(source, target)]
        ratio = edge["traffic"] / edge["capacity"] if edge["capacity"] else 0.0
        edge["congestion"] = ratio
        edge["travel_time"] = edge["free_flow_time"] * (1.0 + 0.15 * ratio ** 4)
        # Common dynamic routing objective. All six pathfinders use this same weight.
        edge["weight"] = (
            1.0 * edge["distance"]
            + 10.0 * edge["travel_time"]
            + 2.0 * edge["congestion"]
        )

    def update_traffic(self, source, target, traffic):
        if (source, target) not in self.edges:
            raise KeyError(f"Unknown edge: {source} -> {target}")
        self.edges[(source, target)]["traffic"] = max(0.0, float(traffic))
        self._recalculate_edge(source, target)

    def set_blocked(self, source, target, blocked=True):
        self.edges[(source, target)]["blocked"] = bool(blocked)

    def get_edge(self, source, target):
        return self.edges.get((source, target))

    def get_neighbors(self, node):
        return [
            target for (source, target), edge in self.edges.items()
            if source == node and not edge.get("blocked", False)
        ]

    def edge_weight(self, source, target, weight="weight"):
        edge = self.get_edge(source, target)
        if edge is None:
            raise KeyError(f"Unknown edge: {source} -> {target}")
        if edge.get("blocked", False):
            return float("inf")
        if weight == "dynamic":
            weight = "weight"
        if weight not in {"distance", "travel_time", "congestion", "weight"}:
            raise ValueError("weight must be distance, travel_time, congestion, weight, or dynamic")
        return edge[weight]

    def route_metrics(self, path):
        distance = travel_time = congestion = 0.0
        for a, b in zip(path, path[1:]):
            edge = self.get_edge(a, b)
            if edge is None or edge.get("blocked", False):
                raise ValueError(f"Invalid/blocked edge in path: {a} -> {b}")
            distance += edge["distance"]
            travel_time += edge["travel_time"]
            congestion += edge["traffic"] / edge["capacity"]
        return {
            "distance": distance,
            "travel_time": travel_time,
            "congestion": congestion,
            "fitness": distance + 10.0 * travel_time + 2.0 * congestion,
        }

    def print_network(self):
        print("\nNodes")
        for node_id, data in self.nodes.items():
            print(f"{node_id}: ({data['x']}, {data['y']})")
        print("\nRoads")
        for (source, target), data in self.edges.items():
            print(
                f"{source} -> {target} | distance={data['distance']:.2f} | "
                f"traffic={data['traffic']:.2f} | time={data['travel_time']:.4f} | "
                f"weight={data['weight']:.4f}"
            )


def create_test_network():
    network = RoadNetwork()
    for node, x, y in [
        ("A", 0, 0), ("B", 1, 0), ("C", 2, 0),
        ("D", 0, 1), ("E", 1, 1), ("F", 2, 1),
        ("G", 0, 2), ("H", 1, 2), ("I", 2, 2),
    ]:
        network.add_node(node, x, y)

    roads = [
        ("A", "B", 1.0, 40.0, 100), ("B", "C", 1.0, 40.0, 100),
        ("D", "E", 1.0, 35.0, 80), ("E", "F", 1.0, 35.0, 80),
        ("G", "H", 1.0, 30.0, 60), ("H", "I", 1.0, 30.0, 60),
        ("A", "D", 1.0, 30.0, 70), ("D", "G", 1.0, 30.0, 70),
        ("B", "E", 1.0, 45.0, 120), ("E", "H", 1.0, 45.0, 120),
        ("C", "F", 1.0, 40.0, 100), ("F", "I", 1.0, 40.0, 100),
    ]
    for source, target, distance, speed, capacity in roads:
        network.add_edge(source, target, distance, speed, capacity)
        network.add_edge(target, source, distance, speed, capacity)
    return network


if __name__ == "__main__":
    network = create_test_network()
    network.update_traffic("B", "E", 100)
    print(network.get_edge("B", "E"))
