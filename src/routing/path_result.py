from dataclasses import dataclass, asdict


@dataclass
class PathResult:
    algorithm: str
    source: str
    target: str
    path: list
    distance: float
    travel_time: float
    congestion: float
    fitness: float
    runtime: float
    history: list

    def to_dict(self):
        return asdict(self)
