import csv
import statistics


CSV_FILE = "results/benchmark_results.csv"


def load_results():
    results = []

    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            results.append({
                "function": row["Function"],
                "algorithm": row["Algorithm"],
                "trial": int(row["Trial"]),
                "best_fitness": float(row["Best Fitness"]),
                "runtime": float(row["Runtime"]),
            })

    return results


def summarize(results):
    fitness = [r["best_fitness"] for r in results]
    runtimes = [r["runtime"] for r in results]

    return {
        "best": min(fitness),
        "mean": statistics.mean(fitness),
        "worst": max(fitness),
        "std": statistics.stdev(fitness),
        "runtime": statistics.mean(runtimes),
    }


def main():

    results = load_results()

    functions = ["Sphere", "Rastrigin", "Rosenbrock"]
    algorithms = ["PSO", "QPSO"]

    print("\n========================================")
    print("        BENCHMARK ANALYSIS")
    print("========================================")

    for function in functions:

        print(f"\n----------------------------------------")
        print(f"{function}")
        print("----------------------------------------")

        for algorithm in algorithms:

            filtered = [
                r for r in results
                if r["function"] == function
                and r["algorithm"] == algorithm
            ]

            summary = summarize(filtered)

            print(f"\n{algorithm}")
            print(f"Best    : {summary['best']:.10f}")
            print(f"Mean    : {summary['mean']:.10f}")
            print(f"Worst   : {summary['worst']:.10f}")
            print(f"Std     : {summary['std']:.10f}")
            print(f"Runtime : {summary['runtime']:.6f} sec")


if __name__ == "__main__":
    main()