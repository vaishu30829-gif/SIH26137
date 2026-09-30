from src.transport.graph import create_test_network
from src.transport.traffic import TrafficManager
from src.routing.pathfinder_manager import PathfinderManager


def main():
    network = create_test_network()
    traffic = TrafficManager(network, mode="simulator", seed=42)

    # Initial heterogeneous traffic state for a meaningful demonstration.
    for source, target, value in [
        ("B", "C", 95), ("C", "B", 95),
        ("C", "F", 80), ("F", "C", 80),
        ("F", "I", 75), ("I", "F", 75),
        ("A", "D", 10), ("D", "A", 10),
        ("D", "G", 10), ("G", "D", 10),
        ("G", "H", 15), ("H", "G", 15),
        ("H", "I", 15), ("I", "H", 15),
    ]:
        traffic.simulator.set_traffic(source, target, value)

    manager = PathfinderManager(particles=12, iterations=20, seed=42)

    print("=" * 70)
    print("QROUTE - ALL PATHFINDERS")
    print("=" * 70)
    print("Traffic mode: simulator")

    for step in range(3):
        if step:
            traffic.update()
            print(f"\nTraffic update {step}: average={traffic.simulator.get_average_traffic():.2f}")

        results = manager.find_all(network, "A", "I")
        best = manager.select_best(results)

        print("\nAlgorithm comparison")
        for name, result in results.items():
            print(
                f"{name:16s} | path={' -> '.join(result['path']):18s} | "
                f"fitness={result['fitness']:.4f} | "
                f"time={result['travel_time']:.4f} | runtime={result['runtime']:.4f}s"
            )
        print(f"\nRECOMMENDED ROUTE: {' -> '.join(best['path'])}")
        print(f"Suggested by: {', '.join(name for name, r in results.items() if r['path'] == best['path'])}")


if __name__ == "__main__":
    main()
