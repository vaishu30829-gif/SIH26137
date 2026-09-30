import random
import time

from src.routing.path_result import PathResult


class ACOPathfinder:
    """Ant Colony Optimization for source-to-target graph pathfinding."""

    def __init__(self, ants=20, iterations=40, alpha=1.0, beta=3.0, evaporation=0.35, seed=42):
        self.ants = ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.random = random.Random(seed)

    def _construct_path(self, network, source, target):
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
            scores = []
            for neighbor in candidates:
                edge = network.get_edge(current, neighbor)
                heuristic = 1.0 / max(edge["weight"], 1e-9)
                pheromone = self.pheromone.get((current, neighbor), 1.0)
                scores.append((neighbor, (pheromone ** self.alpha) * (heuristic ** self.beta)))
            total = sum(score for _, score in scores)
            if total <= 0:
                current = self.random.choice(candidates)
            else:
                r = self.random.random() * total
                cumulative = 0.0
                current = candidates[-1]
                for neighbor, score in scores:
                    cumulative += score
                    if r <= cumulative:
                        current = neighbor
                        break
            path.append(current)
            visited.add(current)
        return None

    def find_path(self, network, source, target, weight="weight"):
        start = time.perf_counter()
        self.pheromone = {edge: 1.0 for edge in network.edges}
        best_path = None
        best_fitness = float("inf")
        history = []

        for _ in range(self.iterations):
            ant_paths = []
            for _ in range(self.ants):
                path = self._construct_path(network, source, target)
                if path:
                    metrics = network.route_metrics(path)
                    ant_paths.append((path, metrics["fitness"]))
                    if metrics["fitness"] < best_fitness:
                        best_path = path
                        best_fitness = metrics["fitness"]

            for edge in self.pheromone:
                self.pheromone[edge] *= (1.0 - self.evaporation)
                self.pheromone[edge] = max(self.pheromone[edge], 1e-6)

            for path, fitness in ant_paths:
                deposit = 1.0 / max(fitness, 1e-9)
                for edge in zip(path, path[1:]):
                    self.pheromone[edge] = self.pheromone.get(edge, 1.0) + deposit

            history.append(best_fitness if best_path else float("inf"))

        if best_path is None:
            raise ValueError(f"ACO could not find a path from {source} to {target}")
        metrics = network.route_metrics(best_path)
        return PathResult("ACO", source, target, best_path, metrics["distance"], metrics["travel_time"], metrics["congestion"], metrics["fitness"], time.perf_counter() - start, history)
