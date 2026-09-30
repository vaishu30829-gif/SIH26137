import random
import time
import statistics
import csv

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.qpso_vrp import QPSOVRP


CUSTOMER_SIZES = [8, 12, 16, 20]

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


def run_trial(
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

    start_time = time.perf_counter()

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=0.75,
        quantum_weight=quantum_weight
    )

    routes, fitness, history = optimizer.optimize(
        verbose=False
    )

    runtime = time.perf_counter() - start_time

    return fitness, runtime


def summarize(results):

    fitness_values = [
        result["fitness"]
        for result in results
    ]

    runtime_values = [
        result["runtime"]
        for result in results
    ]

    return {
        "best": min(fitness_values),
        "mean": statistics.mean(fitness_values),
        "worst": max(fitness_values),
        "std": statistics.stdev(fitness_values),
        "runtime": statistics.mean(runtime_values)
    }


def main():

    all_results = []

    print("=" * 80)
    print(
        "     QPSO vs DYNAMIC QUANTUM-GUIDED QPSO - VRP SCALABILITY"
    )
    print("=" * 80)

    print(
        f"Customer sizes: {CUSTOMER_SIZES}"
    )

    print(
        f"Trials: {TRIALS} | "
        f"Particles: {PARTICLES} | "
        f"Iterations: {ITERATIONS}"
    )

    print()

    for num_customers in CUSTOMER_SIZES:

        print("-" * 80)
        print(
            f"Testing {num_customers} customers"
        )
        print("-" * 80)

        classical_results = []
        quantum_results = []

        for trial in range(TRIALS):

            seed = (
                1000
                + num_customers * 100
                + trial
            )

            classical_fitness, classical_runtime = run_trial(
                seed=seed,
                num_customers=num_customers,
                quantum_weight=0.0
            )

            quantum_fitness, quantum_runtime = run_trial(
                seed=seed,
                num_customers=num_customers,
                quantum_weight=QUANTUM_WEIGHT
            )

            classical_results.append({
                "fitness": classical_fitness,
                "runtime": classical_runtime
            })

            quantum_results.append({
                "fitness": quantum_fitness,
                "runtime": quantum_runtime
            })

            print(
                f"Trial {trial + 1:02d} | "
                f"QPSO = {classical_fitness:.6f} | "
                f"Dynamic Quantum-QPSO = {quantum_fitness:.6f}"
            )

        classical_summary = summarize(
            classical_results
        )

        quantum_summary = summarize(
            quantum_results
        )

        all_results.append({
            "customers": num_customers,
            "algorithm": "QPSO",
            **classical_summary
        })

        all_results.append({
            "customers": num_customers,
            "algorithm": "Dynamic Quantum-QPSO",
            **quantum_summary
        })

        print()

        print(
            f"{num_customers} Customers - QPSO"
        )

        print(
            f"Best:    {classical_summary['best']:.6f}"
        )
        print(
            f"Mean:    {classical_summary['mean']:.6f}"
        )
        print(
            f"Worst:   {classical_summary['worst']:.6f}"
        )
        print(
            f"Std:     {classical_summary['std']:.6f}"
        )
        print(
            f"Runtime: {classical_summary['runtime']:.6f} s"
        )

        print()

        print(
            f"{num_customers} Customers - "
            f"Dynamic Quantum-QPSO"
        )

        print(
            f"Best:    {quantum_summary['best']:.6f}"
        )
        print(
            f"Mean:    {quantum_summary['mean']:.6f}"
        )
        print(
            f"Worst:   {quantum_summary['worst']:.6f}"
        )
        print(
            f"Std:     {quantum_summary['std']:.6f}"
        )
        print(
            f"Runtime: {quantum_summary['runtime']:.6f} s"
        )

    output_file = (
        "results/"
        "dynamic_quantum_qpso_vrp_scalability.csv"
    )

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Customers",
            "Algorithm",
            "Best",
            "Mean",
            "Worst",
            "Std",
            "Runtime"
        ])

        for result in all_results:

            writer.writerow([
                result["customers"],
                result["algorithm"],
                result["best"],
                result["mean"],
                result["worst"],
                result["std"],
                result["runtime"]
            ])

    print()
    print("=" * 80)
    print(
        f"Results saved to: {output_file}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()