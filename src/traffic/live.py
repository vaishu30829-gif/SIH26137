import json
from urllib.request import Request, urlopen

from src.traffic.base import TrafficProvider


class LiveTrafficProvider(TrafficProvider):
    """Provider adapter for a normalized external traffic feed.

    Expected JSON:
    {"edges": [{"source":"B","target":"E","traffic":620}, ...]}
    """

    def __init__(self, network, url=None, timeout=5):
        self.network = network
        self.url = url
        self.timeout = timeout

    def apply_snapshot(self, snapshot):
        edges = snapshot.get("edges", snapshot) if isinstance(snapshot, dict) else snapshot
        for item in edges:
            self.network.update_traffic(item["source"], item["target"], item["traffic"])

    def fetch_and_apply(self, url=None):
        endpoint = url or self.url
        if not endpoint:
            raise ValueError("A live traffic URL is required")
        request = Request(endpoint, headers={"Accept": "application/json", "User-Agent": "QRoute/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        self.apply_snapshot(payload)
        return payload

    def apply(self, network):
        self.fetch_and_apply()
