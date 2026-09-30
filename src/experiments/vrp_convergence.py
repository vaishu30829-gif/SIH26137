import random
import csv

from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp
from src.vrp.qpso_vrp import QPSOVRP
from src.vrp.pso_vrp import PSOVRP


TRIALS = 10
PARTICLES = 20
ITERATIONS = 50


def create_problem():
    network = create_test_network()
    problem = create_test_vrp(network)

    network.update_traffic("B", "C", 95)
    network.update_traffic("C", "B", 95)

    network.update_traffic("C", "F", 80)
    network.update_traffic("F", "C", 80)

    network.update_traffic("F", "I", 75)
    network.update_traffic("I", "F", 75)

    network.update_traffic("A", "D", 10)
    network.update_traffic("D", "A", 10)

    network.update_traffic("D", "G", 10)
    network.update_traffic("G", "D", 10)

    network.update_traffic("G", "H", 15)
    network.update_traffic("H", "G", 15)

    network.update_traffic("H", "I", 15)
    network.update_traffic("I", "H", 15)

    return network, problem


def run_pso(seed):
    random.seed(seed)

    network, problem = create_problem()

    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=PARTICLES,
        iterations=ITERATIONS,
    )

    _, _, history = optimizer.optimize()

    return history


def run_qpso(seed):
    random.seed(seed)

    network, problem = create_problem()

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
    )

    _, _, history = optimizer.optimize()

    return history


if __name__ == "__main__":

    print("=" * 60)
    print("       PSO vs QPSO VRP CONVERGENCE")
    print("=" * 60)

    pso_histories = []
    qpso_histories = []

    for trial in range(1, TRIALS + 1):

        seed = 1000 + trial

        print(f"\nTrial {trial}/{TRIALS}")

        pso_history = run_pso(seed)
        qpso_history = run_qpso(seed)

        pso_histories.append(pso_history)
        qpso_histories.append(qpso_history)

    # Calculate average fitness at every iteration
    avg_pso = []
    avg_qpso = []

    for i in range(ITERATIONS):

        pso_values = [
            history[i]
            for history in pso_histories
        ]

        qpso_values = [
            history[i]
            for history in qpso_histories
        ]

        avg_pso.append(
            sum(pso_values) / len(pso_values)
        )

        avg_qpso.append(
            sum(qpso_values) / len(qpso_values)
        )

    # Save convergence data
    with open(
        "results/vrp_convergence.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Iteration",
            "PSO",
            "QPSO"
        ])

        for i in range(ITERATIONS):

            writer.writerow([
                i + 1,
                avg_pso[i],
                avg_qpso[i]
            ])

    print("\nConvergence data saved to:")
    print("results/vrp_convergence.csv")

    print("\nAverage convergence:")
    print(
        f"Iteration 1  | "
        f"PSO = {avg_pso[0]:.6f} | "
        f"QPSO = {avg_qpso[0]:.6f}"
    )

    print(
        f"Iteration 50 | "
        f"PSO = {avg_pso[-1]:.6f} | "
        f"QPSO = {avg_qpso[-1]:.6f}"
    )