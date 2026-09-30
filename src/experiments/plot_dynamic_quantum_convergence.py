import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = (
    "results/"
    "dynamic_quantum_qpso_vrp_convergence.csv"
)

OUTPUT_DIR = "results/plots"


def plot_convergence(num_customers):

    df = pd.read_csv(INPUT_FILE)

    data = df[
        df["Customers"] == num_customers
    ]

    plt.figure(figsize=(8, 5))

    plt.plot(
        data["Iteration"],
        data["QPSO"],
        label="QPSO"
    )

    plt.plot(
        data["Iteration"],
        data["Dynamic_Quantum_QPSO"],
        label="Dynamic Quantum-QPSO"
    )

    plt.xlabel("Iteration")
    plt.ylabel("Mean Best Fitness")

    plt.title(
        f"VRP Convergence - {num_customers} Customers"
    )

    plt.legend()
    plt.grid(True)

    output_file = (
        f"{OUTPUT_DIR}/"
        f"convergence_{num_customers}_customers.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


def main():

    plot_convergence(8)
    plot_convergence(20)

    print()
    print("=" * 60)
    print("CONVERGENCE GRAPHS GENERATED")
    print("=" * 60)


if __name__ == "__main__":
    main()