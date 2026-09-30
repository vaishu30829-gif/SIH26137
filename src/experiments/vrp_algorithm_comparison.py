import csv
import os
import random
import time
import io
from contextlib import redirect_stdout
from statistics import mean, stdev

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.pso_vrp import PSOVRP
from src.vrp.qpso_vrp import QPSOVRP


# ============================================================
# CONFIGURATION
# ============================================================

TRIALS = 10
PARTICLES = 20
ITERATIONS = 50

PSO_W = 0.7
PSO_C1 = 1.5
PSO_C2 = 1.5

QPSO_ALPHA = 0.75
QUANTUM_WEIGHT = 0.30

RESULTS_DIR = "results"
OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "vrp_algorithm_comparison.csv"
)


# ============================================================
# CREATE IDENTICAL NETWORK + VRP
# ============================================================

def create_experiment_instance():
    """
    Create a fresh VRP instance with the same
    heterogeneous traffic conditions used by
    the PSO/QPSO experiments.
    """

    network = create_test_network()

    problem = create_test_vrp(
        network
    )

    # --------------------------------------------------------
    # Congested corridors
    # --------------------------------------------------------

    network.update_traffic(
        "B", "C", 95
    )

    network.update_traffic(
        "C", "B", 95
    )

    network.update_traffic(
        "C", "F", 80
    )

    network.update_traffic(
        "F", "C", 80
    )

    network.update_traffic(
        "F", "I", 75
    )

    network.update_traffic(
        "I", "F", 75
    )

    # --------------------------------------------------------
    # Relatively uncongested alternative corridor
    # --------------------------------------------------------

    network.update_traffic(
        "A", "D", 10
    )

    network.update_traffic(
        "D", "A", 10
    )

    network.update_traffic(
        "D", "G", 10
    )

    network.update_traffic(
        "G", "D", 10
    )

    network.update_traffic(
        "G", "H", 15
    )

    network.update_traffic(
        "H", "G", 15
    )

    network.update_traffic(
        "H", "I", 15
    )

    network.update_traffic(
        "I", "H", 15
    )

    return problem, network


# ============================================================
# RUN PSO
# ============================================================

def run_pso(seed):
    """
    Run one PSO-VRP trial.
    """

    random.seed(seed)

    problem, network = (
        create_experiment_instance()
    )

    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=PARTICLES,
        iterations=ITERATIONS,
        w=PSO_W,
        c1=PSO_C1,
        c2=PSO_C2
    )

    # PSOVRP prints every iteration.
    # Suppress those prints during benchmarking.
    output_buffer = io.StringIO()

    start_time = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    end_time = time.perf_counter()

    runtime = (
        end_time - start_time
    )

    return {
        "algorithm": "PSO",
        "best_fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# RUN QPSO
# ============================================================

def run_qpso(seed):
    """
    Run one classical QPSO-VRP trial.
    """

    random.seed(seed)

    problem, network = (
        create_experiment_instance()
    )

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=QPSO_ALPHA,
        quantum_weight=0.0
    )

    # quantum_weight=0.0 means this experiment
    # represents classical QPSO without quantum guidance.

    output_buffer = io.StringIO()

    start_time = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    end_time = time.perf_counter()

    runtime = (
        end_time - start_time
    )

    return {
        "algorithm": "QPSO",
        "best_fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# RUN QUANTUM-GUIDED QPSO
# ============================================================

def run_quantum_qpso(seed):
    """
    Run one Quantum-Guided QPSO-VRP trial.
    """

    random.seed(seed)

    problem, network = (
        create_experiment_instance()
    )

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=QPSO_ALPHA,
        quantum_weight=QUANTUM_WEIGHT
    )

    output_buffer = io.StringIO()

    start_time = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    end_time = time.perf_counter()

    runtime = (
        end_time - start_time
    )

    return {
        "algorithm": "Quantum-QPSO",
        "best_fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(values):

    if len(values) > 1:
        standard_deviation = stdev(
            values
        )
    else:
        standard_deviation = 0.0

    return {
        "best": min(values),
        "mean": mean(values),
        "worst": max(values),
        "std": standard_deviation
    }


# ============================================================
# SAVE CSV
# ============================================================

def save_results(rows):

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    fieldnames = [
        "algorithm",
        "trial",
        "best_fitness",
        "runtime"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ============================================================
# MAIN EXPERIMENT
# ============================================================

def main():

    print("=" * 70)
    print(
        "       PSO vs QPSO vs QUANTUM-GUIDED QPSO"
    )
    print(
        "                 VRP BENCHMARK"
    )
    print("=" * 70)

    print()

    print(
        f"Trials       : {TRIALS}"
    )

    print(
        f"Particles    : {PARTICLES}"
    )

    print(
        f"Iterations   : {ITERATIONS}"
    )

    print(
        f"QPSO alpha   : {QPSO_ALPHA}"
    )

    print(
        f"Quantum wt   : {QUANTUM_WEIGHT}"
    )

    print()

    # --------------------------------------------------------
    # Store all trial results
    # --------------------------------------------------------

    all_rows = []

    algorithm_results = {
        "PSO": [],
        "QPSO": [],
        "Quantum-QPSO": []
    }

    # --------------------------------------------------------
    # Run trials
    # --------------------------------------------------------

    for trial in range(
        1,
        TRIALS + 1
    ):

        print(
            f"Trial {trial:02d}/{TRIALS}"
        )

        # Same base seed for all three algorithms.
        #
        # Each algorithm gets the same initial random
        # sequence before its own run.
        seed = 1000 + trial

        # ----------------------------------------------------
        # PSO
        # ----------------------------------------------------

        pso_result = run_pso(
            seed
        )

        algorithm_results[
            "PSO"
        ].append(
            pso_result
        )

        all_rows.append({
            "algorithm": "PSO",
            "trial": trial,
            "best_fitness":
                pso_result["best_fitness"],
            "runtime":
                pso_result["runtime"]
        })

        print(
            f"  PSO          : "
            f"{pso_result['best_fitness']:.6f} "
            f"({pso_result['runtime']:.4f}s)"
        )

        # ----------------------------------------------------
        # QPSO
        # ----------------------------------------------------

        qpso_result = run_qpso(
            seed
        )

        algorithm_results[
            "QPSO"
        ].append(
            qpso_result
        )

        all_rows.append({
            "algorithm": "QPSO",
            "trial": trial,
            "best_fitness":
                qpso_result["best_fitness"],
            "runtime":
                qpso_result["runtime"]
        })

        print(
            f"  QPSO         : "
            f"{qpso_result['best_fitness']:.6f} "
            f"({qpso_result['runtime']:.4f}s)"
        )

        # ----------------------------------------------------
        # Quantum-Guided QPSO
        # ----------------------------------------------------

        quantum_result = run_quantum_qpso(
            seed
        )

        algorithm_results[
            "Quantum-QPSO"
        ].append(
            quantum_result
        )

        all_rows.append({
            "algorithm": "Quantum-QPSO",
            "trial": trial,
            "best_fitness":
                quantum_result["best_fitness"],
            "runtime":
                quantum_result["runtime"]
        })

        print(
            f"  Quantum-QPSO: "
            f"{quantum_result['best_fitness']:.6f} "
            f"({quantum_result['runtime']:.4f}s)"
        )

        print()

    # --------------------------------------------------------
    # Save raw results
    # --------------------------------------------------------

    save_results(
        all_rows
    )

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    print("=" * 70)
    print("                  FINAL RESULTS")
    print("=" * 70)

    print()

    print(
        f"{'Algorithm':<20}"
        f"{'Best':>14}"
        f"{'Mean':>14}"
        f"{'Worst':>14}"
        f"{'Std':>14}"
        f"{'Runtime':>14}"
    )

    print("-" * 90)

    summary_rows = []

    for algorithm in [
        "PSO",
        "QPSO",
        "Quantum-QPSO"
    ]:

        results = (
            algorithm_results[
                algorithm
            ]
        )

        fitness_values = [
            result["best_fitness"]
            for result in results
        ]

        runtime_values = [
            result["runtime"]
            for result in results
        ]

        statistics = calculate_statistics(
            fitness_values
        )

        average_runtime = mean(
            runtime_values
        )

        print(
            f"{algorithm:<20}"
            f"{statistics['best']:>14.6f}"
            f"{statistics['mean']:>14.6f}"
            f"{statistics['worst']:>14.6f}"
            f"{statistics['std']:>14.6f}"
            f"{average_runtime:>14.4f}"
        )

        summary_rows.append({
            "algorithm": algorithm,
            "best": statistics["best"],
            "mean": statistics["mean"],
            "worst": statistics["worst"],
            "std": statistics["std"],
            "runtime": average_runtime
        })

    # --------------------------------------------------------
    # Best routes from each algorithm
    # --------------------------------------------------------

    print()

    print("=" * 70)
    print("              BEST ROUTES FOUND")
    print("=" * 70)

    for algorithm in [
        "PSO",
        "QPSO",
        "Quantum-QPSO"
    ]:

        results = (
            algorithm_results[
                algorithm
            ]
        )

        best_result = min(
            results,
            key=lambda result:
                result["best_fitness"]
        )

        print()

        print(
            f"{algorithm}:"
        )

        print(
            f"Fitness: "
            f"{best_result['best_fitness']:.6f}"
        )

        print(
            "Routes:"
        )

        for index, route in enumerate(
            best_result["routes"],
            start=1
        ):

            print(
                f"  Vehicle {index}: "
                f"{route}"
            )

    # --------------------------------------------------------
    # Output file
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        f"Raw results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()