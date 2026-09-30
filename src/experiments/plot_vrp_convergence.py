import pandas as pd
import matplotlib.pyplot as plt

# Load convergence results
df = pd.read_csv("results/vrp_convergence.csv")

plt.figure(figsize=(10, 6))

plt.plot(
    df["Iteration"],
    df["PSO"],
    label="PSO",
    linewidth=2
)

plt.plot(
    df["Iteration"],
    df["QPSO"],
    label="QPSO",
    linewidth=2
)

plt.xlabel("Iteration")
plt.ylabel("Best Fitness")
plt.title("PSO vs QPSO Convergence on VRP")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "results/plots/vrp_convergence.png",
    dpi=300
)

plt.show()