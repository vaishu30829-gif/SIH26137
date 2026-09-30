import random


class DifferentialEvolution:
    def __init__(
        self,
        objective_function,
        dimensions,
        population_size=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
        mutation_factor=0.8,
        crossover_rate=0.9,
    ):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.population_size = population_size
        self.iterations = iterations
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.mutation_factor = mutation_factor
        self.crossover_rate = crossover_rate

    def create_individual(self):
        return [
            random.uniform(
                self.lower_bound,
                self.upper_bound
            )
            for _ in range(self.dimensions)
        ]

    def create_population(self):
        return [
            self.create_individual()
            for _ in range(self.population_size)
        ]

    def optimize(self, verbose=True):
        population = self.create_population()

        fitness_values = [
            self.objective_function(individual)
            for individual in population
        ]

        best_index = min(
            range(self.population_size),
            key=lambda i: fitness_values[i]
        )

        best_position = population[best_index].copy()
        best_value = fitness_values[best_index]

        history = []

        for iteration in range(self.iterations):

            new_population = []

            for i in range(self.population_size):

                candidates = [
                    index
                    for index in range(self.population_size)
                    if index != i
                ]

                a, b, c = random.sample(candidates, 3)

                # Differential mutation
                mutant = []

                for dimension in range(self.dimensions):
                    value = (
                        population[a][dimension]
                        + self.mutation_factor
                        * (
                            population[b][dimension]
                            - population[c][dimension]
                        )
                    )

                    value = max(
                        self.lower_bound,
                        min(self.upper_bound, value)
                    )

                    mutant.append(value)

                # Binomial crossover
                trial = []

                forced_dimension = random.randrange(
                    self.dimensions
                )

                for dimension in range(self.dimensions):

                    if (
                        random.random() < self.crossover_rate
                        or dimension == forced_dimension
                    ):
                        trial.append(mutant[dimension])
                    else:
                        trial.append(population[i][dimension])

                trial_value = self.objective_function(trial)

                # Selection
                if trial_value <= fitness_values[i]:
                    new_population.append(trial)
                    fitness_values[i] = trial_value

                    if trial_value < best_value:
                        best_value = trial_value
                        best_position = trial.copy()

                else:
                    new_population.append(
                        population[i].copy()
                    )

            population = new_population

            history.append(best_value)

            if verbose:
                print(
                    f"Iteration {iteration + 1:03d}: "
                    f"best = {best_value:.10f}"
                )

        return best_position, best_value, history


def sphere(position):
    return sum(x ** 2 for x in position)


if __name__ == "__main__":

    optimizer = DifferentialEvolution(
        objective_function=sphere,
        dimensions=5,
        population_size=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
    )

    best_position, best_value, history = optimizer.optimize()

    print("\nFinal result")
    print("Best position:", best_position)
    print("Best fitness:", best_value)