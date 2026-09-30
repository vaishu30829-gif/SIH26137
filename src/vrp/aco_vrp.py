import random
import time

from src.vrp.decoder import split_into_routes
from src.vrp.fitness import calculate_fitness


class ACOVRP:
    """Ant Colony Optimization for the capacitated VRP layer."""

    def __init__(self, problem, network, ants=20, iterations=40, alpha=1.0, beta=2.0, evaporation=0.25, seed=42):
        self.problem = problem
        self.network = network
        self.ants = ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.random = random.Random(seed)
        self.history = []
        self.best_routes = None
        self.best_fitness = float("inf")

        ids = [c.customer_id for c in problem.customers]
        self.pheromone = {(a, b): 1.0 for a in ids for b in ids if a != b}

    def _construct_ordering(self):
        ids = [c.customer_id for c in self.problem.customers]
        current = self.random.choice(ids)
        ordering = [current]
        remaining = set(ids) - {current}
        while remaining:
            candidates = list(remaining)
            scores = []
            for nxt in candidates:
                pheromone = self.pheromone.get((current, nxt), 1.0)
                a = next(c for c in self.problem.customers if c.customer_id == current)
                b = next(c for c in self.problem.customers if c.customer_id == nxt)
                na = self.network.nodes[a.node]
                nb = self.network.nodes[b.node]
                distance = ((na["x"] - nb["x"]) ** 2 + (na["y"] - nb["y"]) ** 2) ** 0.5
                heuristic = 1.0 / max(distance, 1e-6)
                scores.append((nxt, pheromone ** self.alpha * heuristic ** self.beta))
            total = sum(score for _, score in scores)
            if total <= 0:
                nxt = self.random.choice(candidates)
            else:
                r = self.random.random() * total
                cumulative = 0.0
                nxt = candidates[-1]
                for candidate, score in scores:
                    cumulative += score
                    if r <= cumulative:
                        nxt = candidate
                        break
            ordering.append(nxt)
            remaining.remove(nxt)
            current = nxt
        return ordering

    def optimize(self, verbose=False):
        start = time.perf_counter()
        for iteration in range(self.iterations):
            solutions = []
            for _ in range(self.ants):
                ordering = self._construct_ordering()
                routes = split_into_routes(ordering, self.problem)
                result = calculate_fitness(self.problem, self.network, routes)
                solutions.append((ordering, routes, result["fitness"]))
                if result["fitness"] < self.best_fitness:
                    self.best_fitness = result["fitness"]
                    self.best_routes = [r[:] for r in routes]
            for edge in self.pheromone:
                self.pheromone[edge] *= (1.0 - self.evaporation)
            for ordering, _, fitness in solutions:
                deposit = 1.0 / max(fitness, 1e-9)
                for a, b in zip(ordering, ordering[1:]):
                    self.pheromone[(a, b)] += deposit
            self.history.append(self.best_fitness)
            if verbose:
                print(f"Iteration {iteration + 1:03d}: best fitness = {self.best_fitness:.6f}")
        return self.best_routes, self.best_fitness, self.history, time.perf_counter() - start
