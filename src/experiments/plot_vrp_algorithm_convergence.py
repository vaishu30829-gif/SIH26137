import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "results/vrp_algorithm_convergence.csv"
OUTPUT_FILE = "results/plots/vrp_algorithm_convergence.png"


df = pd.read_csv(INPUT_FILE)

# Average convergence across the 10 trials
mean_history = (
    df.groupby(["algorithm", "iteration"])["best_fitness"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(9, 5))

for algorithm in ["PSO", "QPSO", "Quantum-QPSO"]:

    data = mean_history[
        mean_history["algorithm"] == algorithm
    ]

    plt.plot(
        data["iteration"],
        data["best_fitness"],
        marker="o",
        markersize=3,
        label=algorithm,
    )

plt.xlabel("Iteration")
plt.ylabel("Mean Best Fitness")
plt.title(
    "VRP Convergence Comparison: PSO vs QPSO vs Quantum-QPSO"
)

plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=200,
)

plt.close()

print(f"Saved: {OUTPUT_FILE}")