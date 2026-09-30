import sys
import os
import statistics
import time
import csv
# Allow Python to find src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pso.pso import PSO
from qpso.qpso import QPSO
from ga.ga import GeneticAlgorithm
from de.de import DifferentialEvolution


# =========================
# Benchmark Functions
# =========================

def sphere(position):
    return sum(x ** 2 for x in position)


def rastrigin(position):
    n = len(position)
    return 10 * n + sum(
        x ** 2 - 10 * __import__("math").cos(2 * __import__("math").pi * x)
        for x in position
    )


def rosenbrock(position):
    return sum(
        100 * (position[i + 1] - position[i] ** 2) ** 2
        + (1 - position[i]) ** 2
        for i in range(len(position) - 1)
    )


# =========================
# Benchmark Configuration
# =========================

DIMENSIONS = 5
PARTICLES = 30
ITERATIONS = 100
TRIALS = 20

BENCHMARKS = [
    ("Sphere", sphere, -5.12, 5.12),
    ("Rastrigin", rastrigin, -5.12, 5.12),
    ("Rosenbrock", rosenbrock, -5.0, 10.0),
]


# =========================
# Run PSO
# =========================

def run_pso(objective, lower_bound, upper_bound):
    optimizer = PSO(
        objective_function=objective,
        dimensions=DIMENSIONS,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )

    start_time = time.perf_counter()

    _, best_value, history = optimizer.optimize(verbose=False)

    runtime = time.perf_counter() - start_time

    return best_value, runtime, history


# =========================
# Run QPSO
# =========================

def run_qpso(objective, lower_bound, upper_bound):
    optimizer = QPSO(
        objective_function=objective,
        dimensions=DIMENSIONS,
        number_of_particles=PARTICLES,
        iterations=ITERATIONS,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        alpha=0.75,
    )

    start_time = time.perf_counter()

    _, best_value, history = optimizer.optimize(verbose=False)

    runtime = time.perf_counter() - start_time

    return best_value, runtime, history
def run_ga(objective, lower_bound, upper_bound):
    optimizer = GeneticAlgorithm(
        objective_function=objective,
        dimensions=DIMENSIONS,
        population_size=PARTICLES,
        iterations=ITERATIONS,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        crossover_rate=0.8,
        mutation_rate=0.1,
        mutation_strength=0.1,
        elite_size=1,
    )

    start_time = time.perf_counter()

    _, best_value, history = optimizer.optimize(
        verbose=False
    )

    runtime = time.perf_counter() - start_time

    return best_value, runtime, history
def run_de(objective, lower_bound, upper_bound):
    optimizer = DifferentialEvolution(
        objective_function=objective,
        dimensions=DIMENSIONS,
        population_size=PARTICLES,
        iterations=ITERATIONS,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        mutation_factor=0.8,
        crossover_rate=0.9,
    )

    start_time = time.perf_counter()

    _, best_value, history = optimizer.optimize(
        verbose=False
    )

    runtime = time.perf_counter() - start_time

    return best_value, runtime, history


def save_results_to_csv(results, filename="results/benchmark_results.csv"):
    os.makedirs("results", exist_ok=True)

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Function",
            "Algorithm",
            "Trial",
            "Best Fitness",
            "Runtime"
        ])

        for result in results:
            writer.writerow([
                result["function"],
                result["algorithm"],
                result["trial"],
                result["best_fitness"],
                result["runtime"]
            ])

    print(f"\nResults saved to: {filename}")



def save_convergence_to_csv(
    convergence_results,
    filename="results/convergence_results.csv"
):
    os.makedirs("results", exist_ok=True)

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Function",
            "Algorithm",
            "Trial",
            "Iteration",
            "Best Fitness"
        ])

        for result in convergence_results:
            for iteration, fitness in enumerate(
                result["history"],
                start=1
            ):
                writer.writerow([
                    result["function"],
                    result["algorithm"],
                    result["trial"],
                    iteration,
                    fitness
                ])

    print(f"Convergence results saved to: {filename}")

# =========================
# Statistical Summary
# =========================

def summarize(results):
    fitness_values = [result[0] for result in results]
    runtimes = [result[1] for result in results]

    return {
        "best": min(fitness_values),
        "mean": statistics.mean(fitness_values),
        "worst": max(fitness_values),
        "std": statistics.stdev(fitness_values)
        if len(fitness_values) > 1
        else 0.0,
        "runtime": statistics.mean(runtimes),
    }


# =========================
# Main Benchmark
# =========================

def main():

    print("\n========================================")
    print("        PSO vs QPSO BENCHMARK")
    print("========================================")

    print(f"Dimensions : {DIMENSIONS}")
    print(f"Particles  : {PARTICLES}")
    print(f"Iterations : {ITERATIONS}")
    print(f"Trials     : {TRIALS}")
    results = []
    convergence_results = []
    for name, objective, lower_bound, upper_bound in BENCHMARKS:

        print("\n\n========================================")
        print(f"Benchmark: {name}")
        print("========================================")

        pso_results = []
        qpso_results = []
        ga_results = []
        de_results = []
        # -------------------------
        # PSO Trials
        # -------------------------

        print("\nRunning PSO...")

        for trial in range(TRIALS):

            best_value, runtime, history = run_pso(
                objective,
                lower_bound,
                upper_bound
            )
            results.append({
                "function":name,
                "algorithm": "PSO",
                "trial": trial + 1,
                "best_fitness": best_value,
                "runtime": runtime,
            })
            convergence_results.append({
                "function": name,
                "algorithm": "PSO",
                "trial": trial + 1,
                "history": history
            })

            pso_results.append(
                (best_value, runtime, history)
            )

            print(
                f"PSO Trial {trial + 1:02d}: "
                f"{best_value:.10f}"
            )

        # -------------------------
        # QPSO Trials
        # -------------------------

        print("\nRunning QPSO...")

        for trial in range(TRIALS):

            best_value, runtime, history = run_qpso(
                objective,
                lower_bound,
                upper_bound
            )
            results.append({
                "function": name,
                "algorithm": "QPSO",
                "trial": trial + 1,
                "best_fitness": best_value,
                "runtime": runtime
            })
            convergence_results.append({
                "function": name,
                "algorithm": "QPSO",
                "trial": trial + 1,
                "history": history
            })

            qpso_results.append(
                (best_value, runtime, history)
            )

            print(
                f"QPSO Trial {trial + 1:02d}: "
                f"{best_value:.10f}"
            )
        print("\nRunning GA...")

        for trial in range(TRIALS):

            best_value, runtime, history = run_ga(
                objective,
                lower_bound,
                upper_bound
            )

            results.append({
                "function": name,
                "algorithm": "GA",
                "trial": trial + 1,
                "best_fitness": best_value,
                "runtime": runtime
            })

            convergence_results.append({
                "function": name,
                "algorithm": "GA",
                "trial": trial + 1,
                "history": history
            })

            ga_results.append(
                (best_value, runtime, history)
            )

            print(
                f"GA Trial {trial + 1:02d}: "
                f"{best_value:.10f}"
            )
        print("\nRunning DE...")

        for trial in range(TRIALS):

            best_value, runtime, history = run_de(
                objective,
                lower_bound,
                upper_bound
            )

            results.append({
                "function": name,
                "algorithm": "DE",
                "trial": trial + 1,
                "best_fitness": best_value,
                "runtime": runtime
            })

            convergence_results.append({
                "function": name,
                "algorithm": "DE",
                "trial": trial + 1,
                "history": history
            })

            de_results.append(
                (best_value, runtime, history)
            )

            print(
                f"DE Trial {trial + 1:02d}: "
                f"{best_value:.10f}"
            )

        # -------------------------
        # Statistics
        # -------------------------

        pso_summary = summarize(pso_results)
        qpso_summary = summarize(qpso_results)
        ga_summary = summarize(ga_results)
        de_summary = summarize(de_results)

        print("\n----------------------------------------")
        print(f"RESULTS: {name}")
        print("----------------------------------------")

        print("\nPSO")
        print(f"Best   : {pso_summary['best']:.10f}")
        print(f"Mean   : {pso_summary['mean']:.10f}")
        print(f"Worst  : {pso_summary['worst']:.10f}")
        print(f"Std    : {pso_summary['std']:.10f}")
        print(f"Runtime: {pso_summary['runtime']:.6f} sec")

        print("\nQPSO")
        print(f"Best   : {qpso_summary['best']:.10f}")
        print(f"Mean   : {qpso_summary['mean']:.10f}")
        print(f"Worst  : {qpso_summary['worst']:.10f}")
        print(f"Std    : {qpso_summary['std']:.10f}")
        print(f"Runtime: {qpso_summary['runtime']:.6f} sec")

        print("\nGA")
        print(f"Best   : {ga_summary['best']:.10f}")
        print(f"Mean   : {ga_summary['mean']:.10f}")
        print(f"Worst  : {ga_summary['worst']:.10f}")
        print(f"Std    : {ga_summary['std']:.10f}")
        print(f"Runtime: {ga_summary['runtime']:.6f} sec")

        print("\nDE")
        print(f"Best   : {de_summary['best']:.10f}")
        print(f"Mean   : {de_summary['mean']:.10f}")
        print(f"Worst  : {de_summary['worst']:.10f}")
        print(f"Std    : {de_summary['std']:.10f}")
        print(f"Runtime: {de_summary['runtime']:.6f} sec")
    save_results_to_csv(results)
    save_convergence_to_csv(convergence_results)
if __name__ == "__main__":
    main()