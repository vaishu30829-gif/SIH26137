from src.traffic.simulator import SimulatorTrafficProvider
from src.traffic.live import LiveTrafficProvider


class TrafficManager:
    def __init__(self, network, mode="simulator", seed=42):
        self.network = network
        self.mode = mode
        self.simulator = SimulatorTrafficProvider(network, seed=seed)
        self.live = LiveTrafficProvider(network)

    def update(self, live_url=None):
        if self.mode == "simulator":
            self.simulator.apply(self.network)
        elif self.mode == "live":
            self.live.fetch_and_apply(live_url)
        else:
            raise ValueError("mode must be 'simulator' or 'live'")

    def set_mode(self, mode):
        if mode not in {"simulator", "live"}:
            raise ValueError("mode must be 'simulator' or 'live'")
        self.mode = mode

    def apply_live_snapshot(self, snapshot):
        self.live.apply_snapshot(snapshot)
        self.mode = "live"
