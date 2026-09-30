from src.transport.graph import create_test_network
from src.transport.traffic import DynamicTraffic


def main():

    network = create_test_network()

    traffic = DynamicTraffic(
        network=network,
        seed=42,
        variation=0.10
    )

    # Initial traffic
    traffic.set_traffic(
        "B",
        "C",
        95
    )

    traffic.set_traffic(
        "C",
        "B",
        95
    )

    traffic.set_traffic(
        "C",
        "F",
        80
    )

    traffic.set_traffic(
        "F",
        "C",
        80
    )

    print("INITIAL STATE")

    traffic.print_state()

    # Simulate traffic changes.
    for iteration in range(1, 6):

        traffic.update()

        print(
            f"\nAfter traffic update "
            f"{iteration}"
        )

        print(
            f"Average traffic: "
            f"{traffic.get_average_traffic():.2f}"
        )

    print()
    print(
        "Traffic simulation completed."
    )


if __name__ == "__main__":
    main()