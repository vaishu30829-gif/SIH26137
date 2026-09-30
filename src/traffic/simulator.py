import random

from src.traffic.base import TrafficProvider


class SimulatorTrafficProvider(TrafficProvider):
    def __init__(self, network, seed=42, variation=0.10, initial_ratio=0.35):
        self.network = network
        self.random = random.Random(seed)
        self.variation = variation
        self.current = {}
        for edge, data in network.edges.items():
            value = data["capacity"] * initial_ratio
            self.current[edge] = value
            network.update_traffic(*edge, value)

    def apply(self, network):
        for edge, current in list(self.current.items()):
            new_value = max(0.0, current * (1.0 + self.random.uniform(-self.variation, self.variation)))
            self.current[edge] = new_value
            network.update_traffic(*edge, new_value)

    def set(self, source, target, traffic):
        value = max(0.0, float(traffic))
        self.current[(source, target)] = value
        self.network.update_traffic(source, target, value)
