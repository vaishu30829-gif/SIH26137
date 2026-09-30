

import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = (
    "results/"
    "dynamic_quantum_qpso_vrp_scalability.csv"
)

OUTPUT_DIR = "results/plots"


def main():

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------
    # 1. Mean Fitness vs Customers
    # --------------------------------------------------

    plt.figure(figsize=(8, 5))

    for algorithm in df["Algorithm"].unique():

        data = df[
            df["Algorithm"] == algorithm
        ]

        plt.plot(
            data["Customers"],
            data["Mean"],
            marker="o",
            label=algorithm
        )

    plt.xlabel("Number of Customers")
    plt.ylabel("Mean Fitness")
    plt.title(
        "Mean Fitness vs Number of Customers"
    )
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"{OUTPUT_DIR}/mean_fitness_scalability.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # --------------------------------------------------
    # 2. Runtime vs Customers
    # --------------------------------------------------

    plt.figure(figsize=(8, 5))

    for algorithm in df["Algorithm"].unique():

        data = df[
            df["Algorithm"] == algorithm
        ]

        plt.plot(
            data["Customers"],
            data["Runtime"],
            marker="o",
            label=algorithm
        )

    plt.xlabel("Number of Customers")
    plt.ylabel("Runtime (seconds)")
    plt.title(
        "Runtime vs Number of Customers"
    )
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"{OUTPUT_DIR}/runtime_scalability.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # --------------------------------------------------
    # 3. Standard Deviation vs Customers
    # --------------------------------------------------

    plt.figure(figsize=(8, 5))

    for algorithm in df["Algorithm"].unique():

        data = df[
            df["Algorithm"] == algorithm
        ]

        plt.plot(
            data["Customers"],
            data["Std"],
            marker="o",
            label=algorithm
        )

    plt.xlabel("Number of Customers")
    plt.ylabel("Standard Deviation")
    plt.title(
        "Optimization Stability vs Number of Customers"
    )
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"{OUTPUT_DIR}/std_scalability.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    print()
    print("=" * 60)
    print("SCALABILITY GRAPHS GENERATED")
    print("=" * 60)

    print(
        "Saved:"
    )

    print(
        "results/plots/"
        "mean_fitness_scalability.png"
    )

    print(
        "results/plots/"
        "runtime_scalability.png"
    )

    print(
        "results/plots/"
        "std_scalability.png"
    )


if __name__ == "__main__":
    main()