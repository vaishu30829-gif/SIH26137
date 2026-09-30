from de import DifferentialEvolution


def rastrigin(position):
    import math

    n = len(position)

    return 10 * n + sum(
        x ** 2 - 10 * math.cos(2 * math.pi * x)
        for x in position
    )


def rosenbrock(position):
    return sum(
        100 * (position[i + 1] - position[i] ** 2) ** 2
        + (1 - position[i]) ** 2
        for i in range(len(position) - 1)
    )


functions = [
    ("Rastrigin", rastrigin, -5.12, 5.12),
    ("Rosenbrock", rosenbrock, -5.0, 10.0),
]


for name, objective, lower, upper in functions:

    print("\n========================================")
    print(f"DE TEST: {name}")
    print("========================================")

    optimizer = DifferentialEvolution(
        objective_function=objective,
        dimensions=5,
        population_size=30,
        iterations=100,
        lower_bound=lower,
        upper_bound=upper,
    )

    best_position, best_value, history = optimizer.optimize(
        verbose=False
    )

    print("Best position:", best_position)
    print("Best fitness:", best_value)