import random


class GeneticAlgorithm:
    def __init__(
        self,
        objective_function,
        dimensions,
        population_size=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
        crossover_rate=0.8,
        mutation_rate=0.1,
        mutation_strength=0.1,
        elite_size=1,
    ):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.population_size = population_size
        self.iterations = iterations
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.elite_size = elite_size

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

    def fitness(self, individual):
        return self.objective_function(individual)

    def tournament_selection(self, population, fitness_values):
        tournament_size = 3

        selected_indices = random.sample(
            range(len(population)),
            tournament_size
        )

        winner = min(
            selected_indices,
            key=lambda i: fitness_values[i]
        )

        return population[winner].copy()

    def crossover(self, parent1, parent2):
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()

        child1 = []
        child2 = []

        for x1, x2 in zip(parent1, parent2):
            alpha = random.random()

            value1 = alpha * x1 + (1 - alpha) * x2
            value2 = alpha * x2 + (1 - alpha) * x1

            child1.append(value1)
            child2.append(value2)

        return child1, child2

    def mutate(self, individual):
        for i in range(self.dimensions):
            if random.random() < self.mutation_rate:

                individual[i] += random.gauss(
                    0,
                    self.mutation_strength
                    * (self.upper_bound - self.lower_bound)
                )

                individual[i] = max(
                    self.lower_bound,
                    min(self.upper_bound, individual[i])
                )

        return individual

    def optimize(self, verbose=True):
        population = self.create_population()

        best_position = None
        best_value = float("inf")

        history = []

        for iteration in range(self.iterations):

            fitness_values = [
                self.fitness(individual)
                for individual in population
            ]

            # Find best individual
            current_best_index = min(
                range(len(population)),
                key=lambda i: fitness_values[i]
            )

            current_best_value = fitness_values[current_best_index]

            if current_best_value < best_value:
                best_value = current_best_value
                best_position = population[
                    current_best_index
                ].copy()

            history.append(best_value)

            if verbose:
                print(
                    f"Iteration {iteration + 1:03d}: "
                    f"best = {best_value:.10f}"
                )

            # Elitism
            ranked_indices = sorted(
                range(len(population)),
                key=lambda i: fitness_values[i]
            )

            new_population = [
                population[i].copy()
                for i in ranked_indices[:self.elite_size]
            ]

            # Generate new population
            while len(new_population) < self.population_size:

                parent1 = self.tournament_selection(
                    population,
                    fitness_values
                )

                parent2 = self.tournament_selection(
                    population,
                    fitness_values
                )

                child1, child2 = self.crossover(
                    parent1,
                    parent2
                )

                child1 = self.mutate(child1)
                child2 = self.mutate(child2)

                new_population.append(child1)

                if len(new_population) < self.population_size:
                    new_population.append(child2)

            population = new_population

        return best_position, best_value, history


def sphere(position):
    return sum(x ** 2 for x in position)


if __name__ == "__main__":

    optimizer = GeneticAlgorithm(
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