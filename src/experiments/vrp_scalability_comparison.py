import csv
import io
import os
import random
import time
from contextlib import redirect_stdout
from statistics import mean, stdev

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.pso_vrp import PSOVRP
from src.vrp.qpso_vrp import QPSOVRP


# ============================================================
# CONFIGURATION
# ============================================================

CUSTOMER_SIZES = [8, 12, 16, 20]

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
    "vrp_scalability_comparison.csv"
)


# ============================================================
# TRAFFIC CONFIGURATION
# ============================================================

def apply_traffic(network):
    """
    Apply the same heterogeneous traffic conditions
    used in the previous PSO/QPSO experiments.
    """

    # Congested corridors
    network.update_traffic("B", "C", 95)
    network.update_traffic("C", "B", 95)

    network.update_traffic("C", "F", 80)
    network.update_traffic("F", "C", 80)

    network.update_traffic("F", "I", 75)
    network.update_traffic("I", "F", 75)

    # Relatively uncongested alternative corridor
    network.update_traffic("A", "D", 10)
    network.update_traffic("D", "A", 10)

    network.update_traffic("D", "G", 10)
    network.update_traffic("G", "D", 10)

    network.update_traffic("G", "H", 15)
    network.update_traffic("H", "G", 15)

    network.update_traffic("H", "I", 15)
    network.update_traffic("I", "H", 15)


# ============================================================
# CREATE EXPERIMENT INSTANCE
# ============================================================

def create_experiment_instance(num_customers):
    """
    Create a fresh network and VRP problem.

    Every algorithm receives a newly created instance
    with identical traffic conditions.
    """

    network = create_test_network()

    problem = create_test_vrp(
        network,
        num_customers=num_customers
    )

    apply_traffic(network)

    return problem, network


# ============================================================
# RUN PSO
# ============================================================

def run_pso(num_customers, seed):

    random.seed(seed)

    problem, network = (
        create_experiment_instance(
            num_customers
        )
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

    output_buffer = io.StringIO()

    start = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    runtime = (
        time.perf_counter() - start
    )

    return {
        "algorithm": "PSO",
        "customers": num_customers,
        "fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# RUN CLASSICAL QPSO
# ============================================================

def run_qpso(num_customers, seed):

    random.seed(seed)

    problem, network = (
        create_experiment_instance(
            num_customers
        )
    )

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=QPSO_ALPHA,
        quantum_weight=0.0
    )

    output_buffer = io.StringIO()

    start = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    runtime = (
        time.perf_counter() - start
    )

    return {
        "algorithm": "QPSO",
        "customers": num_customers,
        "fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# RUN QUANTUM-GUIDED QPSO
# ============================================================

def run_quantum_qpso(num_customers, seed):

    random.seed(seed)

    problem, network = (
        create_experiment_instance(
            num_customers
        )
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

    start = time.perf_counter()

    with redirect_stdout(output_buffer):

        best_routes, best_fitness, history = (
            optimizer.optimize()
        )

    runtime = (
        time.perf_counter() - start
    )

    return {
        "algorithm": "Quantum-QPSO",
        "customers": num_customers,
        "fitness": best_fitness,
        "runtime": runtime,
        "history": history,
        "routes": best_routes
    }


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(values):

    if len(values) > 1:
        std_value = stdev(values)
    else:
        std_value = 0.0

    return {
        "best": min(values),
        "mean": mean(values),
        "worst": max(values),
        "std": std_value,
        "runtime": mean(values)
    }


# ============================================================
# SAVE RAW RESULTS
# ============================================================

def save_results(rows):

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    fieldnames = [
        "customers",
        "algorithm",
        "trial",
        "fitness",
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
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "        PSO vs QPSO vs QUANTUM-QPSO"
    )
    print(
        "             VRP SCALABILITY"
    )
    print("=" * 80)

    print()

    print(
        f"Customer sizes : {CUSTOMER_SIZES}"
    )

    print(
        f"Trials         : {TRIALS}"
    )

    print(
        f"Particles      : {PARTICLES}"
    )

    print(
        f"Iterations     : {ITERATIONS}"
    )

    print(
        f"QPSO alpha     : {QPSO_ALPHA}"
    )

    print(
        f"Quantum weight : {QUANTUM_WEIGHT}"
    )

    print()

    raw_results = []

    summary = {}

    # ========================================================
    # CUSTOMER SIZES
    # ========================================================

    for num_customers in CUSTOMER_SIZES:

        print("=" * 80)

        print(
            f"CUSTOMERS: {num_customers}"
        )

        print("=" * 80)

        summary[num_customers] = {}

        for algorithm in [
            "PSO",
            "QPSO",
            "Quantum-QPSO"
        ]:

            summary[num_customers][algorithm] = []

        # ----------------------------------------------------
        # TRIALS
        # ----------------------------------------------------

        for trial in range(
            1,
            TRIALS + 1
        ):

            print(
                f"\nTrial {trial:02d}/{TRIALS}"
            )

            seed = (
                10000
                + num_customers * 100
                + trial
            )

            # =================================================
            # PSO
            # =================================================

            pso = run_pso(
                num_customers,
                seed
            )

            summary[num_customers][
                "PSO"
            ].append(pso)

            raw_results.append({
                "customers": num_customers,
                "algorithm": "PSO",
                "trial": trial,
                "fitness": pso["fitness"],
                "runtime": pso["runtime"]
            })

            print(
                f"  PSO           "
                f"{pso['fitness']:.6f} "
                f"({pso['runtime']:.4f}s)"
            )

            # =================================================
            # QPSO
            # =================================================

            qpso = run_qpso(
                num_customers,
                seed
            )

            summary[num_customers][
                "QPSO"
            ].append(qpso)

            raw_results.append({
                "customers": num_customers,
                "algorithm": "QPSO",
                "trial": trial,
                "fitness": qpso["fitness"],
                "runtime": qpso["runtime"]
            })

            print(
                f"  QPSO          "
                f"{qpso['fitness']:.6f} "
                f"({qpso['runtime']:.4f}s)"
            )

            # =================================================
            # QUANTUM-QPSO
            # =================================================

            quantum = run_quantum_qpso(
                num_customers,
                seed
            )

            summary[num_customers][
                "Quantum-QPSO"
            ].append(quantum)

            raw_results.append({
                "customers": num_customers,
                "algorithm": "Quantum-QPSO",
                "trial": trial,
                "fitness": quantum["fitness"],
                "runtime": quantum["runtime"]
            })

            print(
                f"  Quantum-QPSO "
                f"{quantum['fitness']:.6f} "
                f"({quantum['runtime']:.4f}s)"
            )

        print()

    # ========================================================
    # SAVE RAW DATA
    # ========================================================

    save_results(
        raw_results
    )

    # ========================================================
    # FINAL SCALABILITY TABLE
    # ========================================================

    print()
    print("=" * 100)
    print(
        "                    SCALABILITY RESULTS"
    )
    print("=" * 100)

    for num_customers in CUSTOMER_SIZES:

        print()
        print(
            f"Customers: {num_customers}"
        )

        print("-" * 100)

        print(
            f"{'Algorithm':<20}"
            f"{'Best':>14}"
            f"{'Mean':>14}"
            f"{'Worst':>14}"
            f"{'Std':>14}"
            f"{'Runtime':>14}"
        )

        print("-" * 100)

        for algorithm in [
            "PSO",
            "QPSO",
            "Quantum-QPSO"
        ]:

            results = (
                summary[
                    num_customers
                ][algorithm]
            )

            fitness_values = [
                item["fitness"]
                for item in results
            ]

            runtime_values = [
                item["runtime"]
                for item in results
            ]

            if len(fitness_values) > 1:
                std_value = stdev(
                    fitness_values
                )
            else:
                std_value = 0.0

            print(
                f"{algorithm:<20}"
                f"{min(fitness_values):>14.6f}"
                f"{mean(fitness_values):>14.6f}"
                f"{max(fitness_values):>14.6f}"
                f"{std_value:>14.6f}"
                f"{mean(runtime_values):>14.4f}"
            )

    # ========================================================
    # SCALABILITY SUMMARY
    # ========================================================

    print()
    print("=" * 100)
    print(
        "                 MEAN FITNESS BY SIZE"
    )
    print("=" * 100)

    print()

    print(
        f"{'Customers':<12}"
        f"{'PSO':>16}"
        f"{'QPSO':>16}"
        f"{'Quantum-QPSO':>18}"
    )

    print("-" * 65)

    for num_customers in CUSTOMER_SIZES:

        values = []

        for algorithm in [
            "PSO",
            "QPSO",
            "Quantum-QPSO"
        ]:

            fitness_values = [
                item["fitness"]
                for item in
                summary[
                    num_customers
                ][algorithm]
            ]

            values.append(
                mean(fitness_values)
            )

        print(
            f"{num_customers:<12}"
            f"{values[0]:>16.6f}"
            f"{values[1]:>16.6f}"
            f"{values[2]:>18.6f}"
        )

    # ========================================================
    # RUNTIME SUMMARY
    # ========================================================

    print()
    print("=" * 100)
    print(
        "                 MEAN RUNTIME BY SIZE"
    )
    print("=" * 100)

    print()

    print(
        f"{'Customers':<12}"
        f"{'PSO':>16}"
        f"{'QPSO':>16}"
        f"{'Quantum-QPSO':>18}"
    )

    print("-" * 65)

    for num_customers in CUSTOMER_SIZES:

        values = []

        for algorithm in [
            "PSO",
            "QPSO",
            "Quantum-QPSO"
        ]:

            runtime_values = [
                item["runtime"]
                for item in
                summary[
                    num_customers
                ][algorithm]
            ]

            values.append(
                mean(runtime_values)
            )

        print(
            f"{num_customers:<12}"
            f"{values[0]:>16.4f}"
            f"{values[1]:>16.4f}"
            f"{values[2]:>18.4f}"
        )

    # ========================================================
    # OUTPUT
    # ========================================================

    print()
    print("=" * 100)

    print(
        "Raw scalability results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 100)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()