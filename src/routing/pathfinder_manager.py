import time

from src.routing.path_result import PathResult
from src.routing.shortest_path import shortest_path, a_star
from src.routing.aco_path import ACOPathfinder
from src.routing.pso_path import PSOPathfinder
from src.routing.qpso_path import QPSOPathfinder


class PathfinderManager:
    """Runs all six pathfinding algorithms on the same live graph state."""

    def __init__(self, particles=20, iterations=40, seed=42):
        self.particles = particles
        self.iterations = iterations
        self.seed = seed

    def _classical_result(self, name, fn, network, source, target):
        start = time.perf_counter()
        path, _ = fn(network, source, target, weight="weight")
        if path is None:
            raise ValueError(f"{name} could not find a path")
        metrics = network.route_metrics(path)
        return PathResult(name, source, target, path, metrics["distance"], metrics["travel_time"], metrics["congestion"], metrics["fitness"], time.perf_counter() - start, [metrics["fitness"]])

    def find_all(self, network, source, target):
        results = [
            self._classical_result("Dijkstra", shortest_path, network, source, target),
            self._classical_result("A*", a_star, network, source, target),
            ACOPathfinder(self.particles, self.iterations, seed=self.seed).find_path(network, source, target),
            PSOPathfinder(self.particles, self.iterations, seed=self.seed + 1).find_path(network, source, target),
            QPSOPathfinder(self.particles, self.iterations, seed=self.seed + 2).find_path(network, source, target),
            __import__("src.routing.quantum_qpso_path", fromlist=["QuantumQPSOPathfinder"]).QuantumQPSOPathfinder(self.particles, self.iterations, seed=self.seed + 3).find_path(network, source, target),
        ]
        return {result.algorithm: result.to_dict() for result in results}

    @staticmethod
    def select_best(results):
        return min(results.values(), key=lambda result: result["fitness"])
