import random

from src.transport import traffic
from src.transport.graph import create_test_network
from src.transport.traffic import DynamicTraffic
from src.vrp.vrp import create_test_vrp
from src.vrp.qpso_vrp import QPSOVRP


CUSTOMERS = 8
PARTICLES = 20
ITERATIONS = 50


def initialize_traffic(network):

    traffic = DynamicTraffic(
        network=network,
        seed=42,
        variation=0.10
    )

    initial_traffic = [
        ("B", "C", 95),
        ("C", "B", 95),

        ("C", "F", 80),
        ("F", "C", 80),

        ("F", "I", 75),
        ("I", "F", 75),

        ("A", "D", 10),
        ("D", "A", 10),

        ("D", "G", 10),
        ("G", "D", 10),

        ("G", "H", 15),
        ("H", "G", 15),

        ("H", "I", 15),
        ("I", "H", 15),
    ]

    for source, target, value in initial_traffic:

        traffic.set_traffic(
            source,
            target,
            value
        )

    return traffic


def main():

    print("=" * 70)
    print("       DYNAMIC TRAFFIC QPSO-VRP")
    print("=" * 70)

    random.seed(42)

    # --------------------------------------------------
    # Create network
    # --------------------------------------------------

    network = create_test_network()

    # --------------------------------------------------
    # Create VRP
    # --------------------------------------------------

    problem = create_test_vrp(
        network,
        num_customers=CUSTOMERS
    )

    # --------------------------------------------------
    # Initialize dynamic traffic
    # --------------------------------------------------

    traffic = initialize_traffic(
        network
    )

    print(
        f"\nCustomers: {CUSTOMERS}"
    )

    print(
        f"Particles: {PARTICLES}"
    )

    print(
        f"Iterations: {ITERATIONS}"
    )

    print(
        f"Initial average traffic: "
        f"{traffic.get_average_traffic():.4f}"
    )

    # --------------------------------------------------
    # Create QPSO
    # --------------------------------------------------

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=0.75,
        quantum_weight=0.30
    )

    # --------------------------------------------------
    # Dynamic optimization loop
    # --------------------------------------------------

    for iteration in range(ITERATIONS):
        # Update traffic before each iteration except the first.
        if iteration > 0:
            traffic.update()
            # Traffic has changed, so stored pbest/gbest
            # values must be evaluated under the new state.
            optimizer.reevaluate_memory()

        routes, fitness, result = optimizer.optimize_iteration()
        print(
            f"Iteration {iteration + 1:02d} | "
            f"Traffic = {traffic.get_average_traffic():.4f} | "
            f"Best fitness = {fitness:.6f}"
        )

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(f"Best fitness: {optimizer.global_best_fitness:.6f}")
    print(f"Best routes: {optimizer.global_best_routes}")
    print()
    print(
        "Dynamic traffic loop verified."
    )


if __name__ == "__main__":
    main()