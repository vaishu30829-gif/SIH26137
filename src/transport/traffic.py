"""Backward-compatible import for the new traffic subsystem."""
from src.traffic.simulator import SimulatorTrafficProvider
from src.traffic.manager import TrafficManager


class DynamicTraffic(SimulatorTrafficProvider):
    def update(self):
        return self.apply(self.network)

    def set_traffic(self, source, target, traffic):
        return self.set(source, target, traffic)

    def get_traffic(self, source, target):
        return self.current.get((source, target), 0.0)

    def get_average_traffic(self):
        return sum(self.current.values()) / len(self.current) if self.current else 0.0

    def snapshot(self):
        return {f"{a}->{b}": v for (a, b), v in self.current.items()}
