import csv
import random
import statistics
import time

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.pso_vrp import PSOVRP
from src.vrp.qpso_vrp import QPSOVRP


# Experiment settings
CUSTOMER_SIZES = [20]
TRIALS = 10

PARTICLES = 20
ITERATIONS = 50


def apply_traffic(network):
    """
    Apply the same heterogeneous traffic conditions
    used in the existing VRP experiments.
    """

    traffic_conditions = [
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

    for source, target, traffic in traffic_conditions:
        network.update_traffic(
            source,
            target,
            traffic
        )


def run_pso(problem, network, seed):
    """
    Run PSO for one trial.
    """

    random.seed(seed)

    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=PARTICLES,
        iterations=ITERATIONS
    )

    start = time.perf_counter()

    best_routes, best_fitness, history = optimizer.optimize()

    runtime = time.perf_counter() - start

    return best_fitness, runtime


def run_qpso(problem, network, seed):
    """
    Run QPSO for one trial.
    """

    random.seed(seed)

    optimizer = QPSOVRP(
        problem=problem,
        network=network
    )

    start = time.perf_counter()

    best_routes, best_fitness, history = optimizer.optimize()

    runtime = time.perf_counter() - start

    return best_fitness, runtime


def summarize(values):
    """
    Calculate summary statistics.
    """

    return {
        "best": min(values),
        "mean": statistics.mean(values),
        "worst": max(values),
        "std": statistics.stdev(values)
        if len(values) > 1
        else 0.0
    }


def main():

    all_results = []

    print("\n" + "=" * 70)
    print("VRP SCALABILITY BENCHMARK")
    print("=" * 70)

    print(
        f"Customer sizes : {CUSTOMER_SIZES}"
    )
    print(
        f"Trials          : {TRIALS}"
    )
    print(
        f"PSO particles   : {PARTICLES}"
    )
    print(
        f"Iterations      : {ITERATIONS}"
    )

    for num_customers in CUSTOMER_SIZES:

        print("\n" + "-" * 70)
        print(
            f"Testing {num_customers} customers"
        )
        print("-" * 70)

        pso_fitnesses = []
        pso_runtimes = []

        qpso_fitnesses = []
        qpso_runtimes = []

        for trial in range(TRIALS):

            seed = 1000 + trial

            # -----------------------------
            # PSO
            # -----------------------------

            network = create_test_network()

            apply_traffic(network)

            problem = create_test_vrp(
                network,
                num_customers=num_customers
            )

            fitness, runtime = run_pso(
                problem,
                network,
                seed
            )

            pso_fitnesses.append(fitness)
            pso_runtimes.append(runtime)

            # -----------------------------
            # QPSO
            # -----------------------------

            network = create_test_network()

            apply_traffic(network)

            problem = create_test_vrp(
                network,
                num_customers=num_customers
            )

            fitness, runtime = run_qpso(
                problem,
                network,
                seed
            )

            qpso_fitnesses.append(fitness)
            qpso_runtimes.append(runtime)

            print(
                f"Trial {trial + 1:02d}/{TRIALS} "
                f"| PSO = {pso_fitnesses[-1]:.6f} "
                f"| QPSO = {qpso_fitnesses[-1]:.6f}"
            )

        # -----------------------------
        # Summary
        # -----------------------------

        pso_summary = summarize(pso_fitnesses)
        qpso_summary = summarize(qpso_fitnesses)

        pso_mean_runtime = statistics.mean(
            pso_runtimes
        )

        qpso_mean_runtime = statistics.mean(
            qpso_runtimes
        )

        print("\nPSO:")
        print(
            f"  Best    : {pso_summary['best']:.6f}"
        )
        print(
            f"  Mean    : {pso_summary['mean']:.6f}"
        )
        print(
            f"  Worst   : {pso_summary['worst']:.6f}"
        )
        print(
            f"  Std     : {pso_summary['std']:.6f}"
        )
        print(
            f"  Runtime : {pso_mean_runtime:.6f} s"
        )

        print("\nQPSO:")
        print(
            f"  Best    : {qpso_summary['best']:.6f}"
        )
        print(
            f"  Mean    : {qpso_summary['mean']:.6f}"
        )
        print(
            f"  Worst   : {qpso_summary['worst']:.6f}"
        )
        print(
            f"  Std     : {qpso_summary['std']:.6f}"
        )
        print(
            f"  Runtime : {qpso_mean_runtime:.6f} s"
        )

        # Store results
        all_results.append({
            "customers": num_customers,

            "pso_best": pso_summary["best"],
            "pso_mean": pso_summary["mean"],
            "pso_worst": pso_summary["worst"],
            "pso_std": pso_summary["std"],
            "pso_runtime": pso_mean_runtime,

            "qpso_best": qpso_summary["best"],
            "qpso_mean": qpso_summary["mean"],
            "qpso_worst": qpso_summary["worst"],
            "qpso_std": qpso_summary["std"],
            "qpso_runtime": qpso_mean_runtime,
        })

    # -----------------------------
    # Save CSV
    # -----------------------------

    output_file = "results/vrp_scalability.csv"

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=all_results[0].keys()
        )

        writer.writeheader()
        writer.writerows(all_results)

    print("\n" + "=" * 70)
    print("SCALABILITY EXPERIMENT COMPLETE")
    print("=" * 70)

    print(
        f"\nResults saved to: {output_file}"
    )


if __name__ == "__main__":
    main()