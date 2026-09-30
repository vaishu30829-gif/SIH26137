import math
import random
import time

from src.routing.path_result import PathResult
from src.routing.pso_path import decode_priority_path


class QPSOPathfinder:
    def __init__(self, particles=20, iterations=40, alpha=0.75, seed=42):
        self.particles = particles
        self.iterations = iterations
        self.alpha = alpha
        self.random = random.Random(seed)

    def find_path(self, network, source, target, weight="weight"):
        start = time.perf_counter()
        nodes = [n for n in network.nodes if n not in {source, target}]
        dimensions = len(nodes)
        positions = [[self.random.random() for _ in nodes] for _ in range(self.particles)]
        pbest = [p[:] for p in positions]
        pbest_fit = [float("inf")] * self.particles
        gbest = positions[0][:]
        gbest_fit = float("inf")
        history = []

        def evaluate(position):
            path = decode_priority_path(network, source, target, dict(zip(nodes, position)))
            if not path:
                return None, float("inf")
            return path, network.route_metrics(path)["fitness"]

        for _ in range(self.iterations):
            mbest = [sum(p[d] for p in pbest) / self.particles for d in range(dimensions)]
            for i in range(self.particles):
                path, fitness = evaluate(positions[i])
                if fitness < pbest_fit[i]:
                    pbest_fit[i] = fitness
                    pbest[i] = positions[i][:]
                if fitness < gbest_fit:
                    gbest_fit = fitness
                    gbest = positions[i][:]
            mbest = [sum(p[d] for p in pbest) / self.particles for d in range(dimensions)]
            for i in range(self.particles):
                for d in range(dimensions):
                    phi = self.random.random()
                    u = max(self.random.random(), 1e-12)
                    attractor = phi * pbest[i][d] + (1.0 - phi) * gbest[d]
                    sign = 1.0 if self.random.random() < 0.5 else -1.0
                    positions[i][d] = max(0.0, min(1.0, attractor + sign * self.alpha * abs(mbest[d] - positions[i][d]) * math.log(1.0 / u)))
            history.append(gbest_fit)

        best_path, _ = evaluate(gbest)
        if not best_path:
            raise ValueError(f"QPSO could not find a path from {source} to {target}")
        metrics = network.route_metrics(best_path)
        return PathResult("QPSO", source, target, best_path, metrics["distance"], metrics["travel_time"], metrics["congestion"], metrics["fitness"], time.perf_counter() - start, history)
