import random
import time

from src.routing.path_result import PathResult


def decode_priority_path(network, source, target, priorities):
    """Decode a continuous priority vector into a simple graph path."""
    current = source
    path = [current]
    visited = {current}
    max_steps = len(network.nodes) + 2

    for _ in range(max_steps):
        if current == target:
            return path
        candidates = [n for n in network.get_neighbors(current) if n not in visited]
        if not candidates:
            return None
        scored = []
        for neighbor in candidates:
            # Lower priority + lower dynamic edge cost + goal proximity is preferred.
            node_priority = priorities.get(neighbor, 0.5)
            target_node = network.nodes[target]
            neighbor_node = network.nodes[neighbor]
            heuristic = ((neighbor_node["x"] - target_node["x"]) ** 2 + (neighbor_node["y"] - target_node["y"]) ** 2) ** 0.5
            score = node_priority + network.edge_weight(current, neighbor, "weight") + 0.25 * heuristic
            scored.append((score, neighbor))
        scored.sort()
        current = scored[0][1]
        path.append(current)
        visited.add(current)
    return None


class PSOPathfinder:
    def __init__(self, particles=20, iterations=40, w=0.72, c1=1.4, c2=1.4, seed=42):
        self.particles = particles
        self.iterations = iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.random = random.Random(seed)

    def find_path(self, network, source, target, weight="weight"):
        start = time.perf_counter()
        nodes = [n for n in network.nodes if n not in {source, target}]
        dimensions = len(nodes)
        positions = [[self.random.random() for _ in nodes] for _ in range(self.particles)]
        velocities = [[self.random.uniform(-0.1, 0.1) for _ in nodes] for _ in range(self.particles)]
        pbest = [p[:] for p in positions]
        pbest_fit = [float("inf")] * self.particles
        gbest = positions[0][:]
        gbest_fit = float("inf")
        history = []

        def evaluate(position):
            priorities = dict(zip(nodes, position))
            path = decode_priority_path(network, source, target, priorities)
            if not path:
                return None, float("inf")
            return path, network.route_metrics(path)["fitness"]

        for _ in range(self.iterations):
            for i in range(self.particles):
                path, fitness = evaluate(positions[i])
                if fitness < pbest_fit[i]:
                    pbest_fit[i] = fitness
                    pbest[i] = positions[i][:]
                if fitness < gbest_fit:
                    gbest_fit = fitness
                    gbest = positions[i][:]
            for i in range(self.particles):
                for d in range(dimensions):
                    r1 = self.random.random()
                    r2 = self.random.random()
                    velocities[i][d] = self.w * velocities[i][d] + self.c1 * r1 * (pbest[i][d] - positions[i][d]) + self.c2 * r2 * (gbest[d] - positions[i][d])
                    positions[i][d] = max(0.0, min(1.0, positions[i][d] + velocities[i][d]))
            history.append(gbest_fit)

        best_path, _ = evaluate(gbest)
        if not best_path:
            raise ValueError(f"PSO could not find a path from {source} to {target}")
        metrics = network.route_metrics(best_path)
        return PathResult("PSO", source, target, best_path, metrics["distance"], metrics["travel_time"], metrics["congestion"], metrics["fitness"], time.perf_counter() - start, history)
