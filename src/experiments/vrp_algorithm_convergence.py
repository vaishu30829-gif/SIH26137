import csv
import os
import random

from src.transport.graph import create_test_network
from src.transport.traffic import DynamicTraffic
from src.vrp.vrp import create_test_vrp
from src.vrp.pso_vrp import PSOVRP
from src.vrp.qpso_vrp import QPSOVRP


CUSTOMERS = 8
PARTICLES = 20
ITERATIONS = 50
TRIALS = 10

OUTPUT_FILE = "results/vrp_algorithm_convergence.csv"


def run_pso(problem, network):
    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=PARTICLES,
        iterations=ITERATIONS,
    )

    routes, fitness, history = optimizer.optimize()
    return history


def run_qpso(problem, network, quantum_weight):
    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        alpha=0.75,
        quantum_weight=quantum_weight,
    )

    routes, fitness, history = optimizer.optimize()
    return history


def main():

    os.makedirs("results", exist_ok=True)

    rows = []

    for trial in range(1, TRIALS + 1):

        print(f"\nTrial {trial}/{TRIALS}")

        # Same network and traffic seed for fair comparison
        random.seed(1000 + trial)

        network = create_test_network()

        traffic = DynamicTraffic(
            network,
            seed=2000 + trial,
            variation=0.10,
        )

        # Apply initial traffic state
        traffic.update()

        problem = create_test_vrp(
            network,
            num_customers=CUSTOMERS,
        )

        # -------------------------
        # PSO
        # -------------------------
        print("Running PSO...")
        pso_history = run_pso(problem, network)

        for iteration, fitness in enumerate(pso_history, start=1):
            rows.append([
                trial,
                iteration,
                "PSO",
                fitness,
            ])

        # -------------------------
        # QPSO
        # -------------------------
        print("Running QPSO...")
        qpso_history = run_qpso(
            problem,
            network,
            quantum_weight=0.0,
        )

        for iteration, fitness in enumerate(qpso_history, start=1):
            rows.append([
                trial,
                iteration,
                "QPSO",
                fitness,
            ])

        # -------------------------
        # Quantum-QPSO
        # -------------------------
        print("Running Quantum-QPSO...")
        quantum_history = run_qpso(
            problem,
            network,
            quantum_weight=0.30,
        )

        for iteration, fitness in enumerate(quantum_history, start=1):
            rows.append([
                trial,
                iteration,
                "Quantum-QPSO",
                fitness,
            ])

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "trial",
            "iteration",
            "algorithm",
            "best_fitness",
        ])

        writer.writerows(rows)

    print("\n" + "=" * 60)
    print("CONVERGENCE EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()