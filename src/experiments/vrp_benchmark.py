import random
import time
import statistics

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

    # Same traffic conditions for every algorithm
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

    start = time.perf_counter()

    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=PARTICLES,
        iterations=ITERATIONS,
    )

    best_routes, best_fitness, history = optimizer.optimize()

    runtime = time.perf_counter() - start

    return best_fitness, runtime


def run_qpso(seed):
    random.seed(seed)

    network, problem = create_problem()

    start = time.perf_counter()

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
    )

    best_routes, best_fitness, history = optimizer.optimize()

    runtime = time.perf_counter() - start

    return best_fitness, runtime


def summarize(name, results, runtimes):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print("Best fitness :", min(results))
    print("Mean fitness :", statistics.mean(results))
    print("Worst fitness:", max(results))

    if len(results) > 1:
        print(
            "Std deviation:",
            statistics.stdev(results)
        )
    else:
        print("Std deviation: 0")

    print(
        "Mean runtime :",
        statistics.mean(runtimes)
    )


if __name__ == "__main__":

    print("=" * 60)
    print("        VRP BENCHMARK: PSO vs QPSO")
    print("=" * 60)

    pso_results = []
    pso_runtimes = []

    qpso_results = []
    qpso_runtimes = []

    for trial in range(1, TRIALS + 1):

        seed = 1000 + trial

        print(
            f"\nTrial {trial}/{TRIALS}"
        )

        # PSO
        pso_fitness, pso_runtime = run_pso(seed)

        pso_results.append(pso_fitness)
        pso_runtimes.append(pso_runtime)

        print(
            f"PSO  fitness = {pso_fitness:.6f}"
        )

        # QPSO
        qpso_fitness, qpso_runtime = run_qpso(seed)

        qpso_results.append(qpso_fitness)
        qpso_runtimes.append(qpso_runtime)

        print(
            f"QPSO fitness = {qpso_fitness:.6f}"
        )

    summarize(
        "PSO RESULTS",
        pso_results,
        pso_runtimes
    )

    summarize(
        "QPSO RESULTS",
        qpso_results,
        qpso_runtimes
    )