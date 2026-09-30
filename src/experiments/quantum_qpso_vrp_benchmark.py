import random
import time
import statistics

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.qpso_vrp import QPSOVRP


TRIALS = 10
PARTICLES = 20
ITERATIONS = 50
QUANTUM_WEIGHT = 0.30


def apply_traffic(network):
    """Apply the same heterogeneous traffic conditions to every trial."""

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


def run_trial(seed, quantum_weight):

    random.seed(seed)

    network = create_test_network()

    problem = create_test_vrp(
        network,
        num_customers=8
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

    return fitness, runtime, history, routes


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

    classical_results = []
    quantum_results = []

    print("=" * 70)
    print("       QPSO vs QUANTUM-GUIDED QPSO - VRP BENCHMARK")
    print("=" * 70)

    print(
        f"Trials: {TRIALS} | "
        f"Particles: {PARTICLES} | "
        f"Iterations: {ITERATIONS}"
    )

    print()

    for trial in range(TRIALS):

        seed = 1000 + trial

        # Classical QPSO
        classical_fitness, classical_runtime, _, _ = run_trial(
            seed=seed,
            quantum_weight=0.0
        )

        classical_results.append({
            "fitness": classical_fitness,
            "runtime": classical_runtime
        })

        # Quantum-guided QPSO
        quantum_fitness, quantum_runtime, _, _ = run_trial(
            seed=seed,
            quantum_weight=QUANTUM_WEIGHT
        )

        quantum_results.append({
            "fitness": quantum_fitness,
            "runtime": quantum_runtime
        })

        print(
            f"Trial {trial + 1:02d} | "
            f"QPSO = {classical_fitness:.6f} | "
            f"Quantum-QPSO = {quantum_fitness:.6f}"
        )

    classical_summary = summarize(
        classical_results
    )

    quantum_summary = summarize(
        quantum_results
    )

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nClassical QPSO-VRP")
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

    print("\nQuantum-Guided QPSO-VRP")
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


if __name__ == "__main__":
    main()