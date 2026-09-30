import csv
import os
import matplotlib.pyplot as plt


CSV_FILE = "results/convergence_results.csv"
OUTPUT_DIR = "results/plots"


def load_convergence_data():
    data = {}

    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            function = row["Function"]
            algorithm = row["Algorithm"]
            trial = int(row["Trial"])
            iteration = int(row["Iteration"])
            fitness = float(row["Best Fitness"])

            key = (function, algorithm, trial)

            if key not in data:
                data[key] = []

            data[key].append((iteration, fitness))

    return data


def calculate_average_convergence(data, function, algorithm):
    trials = []

    for (func, alg, trial), history in data.items():
        if func == function and alg == algorithm:
            history.sort()
            trials.append([fitness for _, fitness in history])

    if not trials:
        return []

    num_iterations = len(trials[0])

    average = []

    for i in range(num_iterations):
        values = [trial[i] for trial in trials]
        average.append(sum(values) / len(values))

    return average


def plot_function(data, function):
    pso = calculate_average_convergence(
        data,
        function,
        "PSO"
    )

    qpso = calculate_average_convergence(
        data,
        function,
        "QPSO"
    )
    ga = calculate_average_convergence(
        data, function, "GA"
    )
    de = calculate_average_convergence(
        data, function, "DE"
        )

    if not pso or not qpso or not ga or not de:
        print(f"No data found for {function}")
        return

    iterations = range(1, len(pso) + 1)

    plt.figure(figsize=(10, 6))

    plt.plot(
        iterations,
        pso,
        label="PSO"
    )

    plt.plot(
        iterations,
        qpso,
        label="QPSO"
    )
    plt.plot(
        iterations,
        ga,
        label="GA"
    )
    plt.plot(
        iterations,
        de,
        label="DE"
    )

    plt.xlabel("Iteration")
    plt.ylabel("Best Fitness")

    plt.title(
        f"PSO vs QPSO vs GA vs DE Convergence - {function}"
    )

    plt.legend()
    plt.grid(True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = os.path.join(
        OUTPUT_DIR,
        f"{function.lower()}_convergence.png"
    )

    plt.savefig(
        filename,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Saved: {filename}")


def main():
    print("\n========================================")
    print("       CONVERGENCE GRAPH GENERATOR")
    print("========================================")

    data = load_convergence_data()

    functions = [
        "Sphere",
        "Rastrigin",
        "Rosenbrock"
    ]

    for function in functions:
        plot_function(data, function)

    print("\nAll convergence graphs generated.")


if __name__ == "__main__":
    main()