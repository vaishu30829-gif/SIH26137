import random
import csv

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.qpso_vrp import QPSOVRP


CUSTOMER_SIZES = [8, 20]

TRIALS = 10
PARTICLES = 20
ITERATIONS = 50
QUANTUM_WEIGHT = 0.30


def apply_traffic(network):

    traffic = [
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

    for source, target, value in traffic:
        network.update_traffic(
            source,
            target,
            value
        )


def run_optimizer(
    seed,
    num_customers,
    quantum_weight
):

    random.seed(seed)

    network = create_test_network()

    problem = create_test_vrp(
        network,
        num_customers=num_customers
    )

    apply_traffic(network)

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=0.75,
        quantum_weight=quantum_weight
    )

    _, _, history = optimizer.optimize(
        verbose=False
    )

    return history


def average_histories(histories):

    averaged = []

    for iteration in range(ITERATIONS):

        values = [
            history[iteration]
            for history in histories
        ]

        averaged.append(
            sum(values) / len(values)
        )

    return averaged


def main():

    all_results = []

    print("=" * 80)
    print(
        " QPSO vs DYNAMIC QUANTUM-GUIDED QPSO - VRP CONVERGENCE"
    )
    print("=" * 80)

    for num_customers in CUSTOMER_SIZES:

        print()
        print("-" * 80)
        print(
            f"Testing {num_customers} customers"
        )
        print("-" * 80)

        classical_histories = []
        quantum_histories = []

        for trial in range(TRIALS):

            seed = (
                2000
                + num_customers * 100
                + trial
            )

            classical_history = run_optimizer(
                seed=seed,
                num_customers=num_customers,
                quantum_weight=0.0
            )

            quantum_history = run_optimizer(
                seed=seed,
                num_customers=num_customers,
                quantum_weight=QUANTUM_WEIGHT
            )

            classical_histories.append(
                classical_history
            )

            quantum_histories.append(
                quantum_history
            )

            print(
                f"Trial {trial + 1:02d} completed"
            )

        classical_average = average_histories(
            classical_histories
        )

        quantum_average = average_histories(
            quantum_histories
        )

        for iteration in range(ITERATIONS):

            all_results.append({
                "Customers": num_customers,
                "Iteration": iteration + 1,
                "QPSO": classical_average[iteration],
                "Dynamic_Quantum_QPSO":
                    quantum_average[iteration]
            })

        print()
        print(
            f"{num_customers} customers:"
        )

        print(
            f"QPSO final mean: "
            f"{classical_average[-1]:.6f}"
        )

        print(
            f"Dynamic Quantum-QPSO final mean: "
            f"{quantum_average[-1]:.6f}"
        )

    output_file = (
        "results/"
        "dynamic_quantum_qpso_vrp_convergence.csv"
    )

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Customers",
                "Iteration",
                "QPSO",
                "Dynamic_Quantum_QPSO"
            ]
        )

        writer.writeheader()

        writer.writerows(
            all_results
        )

    print()
    print("=" * 80)
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()