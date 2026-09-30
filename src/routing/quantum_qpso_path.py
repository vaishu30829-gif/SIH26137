import math
import random
import time

from src.routing.path_result import PathResult
from src.routing.pso_path import decode_priority_path


class QuantumQPSOPathfinder:
    """QPSO path search with Qiskit-generated quantum guidance."""

    def __init__(self, particles=20, iterations=40, alpha=0.75, quantum_weight=0.30, seed=42, shots=32):
        self.particles = particles
        self.iterations = iterations
        self.alpha = alpha
        self.quantum_weight = quantum_weight
        self.random = random.Random(seed)
        self.shots = shots

    def _quantum_guidance(self, dimensions):
        from qiskit import QuantumCircuit
        from qiskit.primitives import StatevectorSampler
        qubits = max(1, math.ceil(math.log2(max(2, dimensions))))
        qc = QuantumCircuit(qubits)
        for q in range(qubits):
            qc.h(q)
        qc.measure_all()
        sampler = StatevectorSampler()
        result = sampler.run([qc], shots=self.shots).result()
        counts = result[0].data.meas.get_counts()
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        values = []
        max_value = (2 ** qubits) - 1
        for bitstring, _ in ranked:
            values.append(int(bitstring, 2) / max_value if max_value else 0.5)
            if len(values) == dimensions:
                break
        while len(values) < dimensions:
            values.append(self.random.random())
        return values

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
            for i in range(self.particles):
                path, fitness = evaluate(positions[i])
                if fitness < pbest_fit[i]:
                    pbest_fit[i] = fitness
                    pbest[i] = positions[i][:]
                if fitness < gbest_fit:
                    gbest_fit = fitness
                    gbest = positions[i][:]

            mbest = [sum(p[d] for p in pbest) / self.particles for d in range(dimensions)]
            quantum = self._quantum_guidance(dimensions)
            for i in range(self.particles):
                for d in range(dimensions):
                    phi = self.random.random()
                    u = max(self.random.random(), 1e-12)
                    attractor = phi * pbest[i][d] + (1.0 - phi) * gbest[d]
                    sign = 1.0 if self.random.random() < 0.5 else -1.0
                    classical_value = attractor + sign * self.alpha * abs(mbest[d] - positions[i][d]) * math.log(1.0 / u)
                    classical_value = max(0.0, min(1.0, classical_value))
                    positions[i][d] = max(0.0, min(1.0, (1.0 - self.quantum_weight) * classical_value + self.quantum_weight * quantum[d]))
            history.append(gbest_fit)

        best_path, _ = evaluate(gbest)
        if not best_path:
            raise ValueError(f"Quantum-QPSO could not find a path from {source} to {target}")
        metrics = network.route_metrics(best_path)
        return PathResult("Quantum-QPSO", source, target, best_path, metrics["distance"], metrics["travel_time"], metrics["congestion"], metrics["fitness"], time.perf_counter() - start, history)
