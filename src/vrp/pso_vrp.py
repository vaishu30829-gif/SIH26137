import random

from src.vrp.decoder import decode_position
from src.vrp.fitness import calculate_fitness
from src.transport.graph import create_test_network
from src.vrp.vrp import create_test_vrp


class PSOVRP:

    def __init__(
        self,
        problem,
        network,
        particles=20,
        iterations=50,
        w=0.7,
        c1=1.5,
        c2=1.5,
    ):
        self.problem = problem
        self.network = network

        self.particles = particles
        self.iterations = iterations

        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.dimensions = len(problem.customers)

        self.positions = []
        self.velocities = []

        self.pbest_positions = []
        self.pbest_fitness = []

        self.gbest_position = None
        self.gbest_fitness = float("inf")
        self.gbest_routes = None

        self.history = []

    def evaluate_particle(self, position):
        routes = decode_position(
            position,
            self.problem
        )

        result = calculate_fitness(
            self.problem,
            self.network,
            routes
        )

        return routes, result

    def initialize(self):

        self.positions = []
        self.velocities = []

        self.pbest_positions = []
        self.pbest_fitness = []

        self.gbest_position = None
        self.gbest_fitness = float("inf")
        self.gbest_routes = None

        for _ in range(self.particles):

            position = [
                random.uniform(0, 1)
                for _ in range(self.dimensions)
            ]

            velocity = [
                random.uniform(-0.1, 0.1)
                for _ in range(self.dimensions)
            ]

            routes, result = self.evaluate_particle(
                position
            )

            fitness = result["fitness"]

            self.positions.append(position)
            self.velocities.append(velocity)

            self.pbest_positions.append(
                position.copy()
            )

            self.pbest_fitness.append(
                fitness
            )

            if fitness < self.gbest_fitness:

                self.gbest_fitness = fitness
                self.gbest_position = position.copy()
                self.gbest_routes = routes

    def optimize(self):

        self.initialize()

        for iteration in range(
            self.iterations
        ):

            for i in range(self.particles):

                for d in range(self.dimensions):

                    r1 = random.random()
                    r2 = random.random()

                    self.velocities[i][d] = (
                        self.w
                        * self.velocities[i][d]
                        + self.c1
                        * r1
                        * (
                            self.pbest_positions[i][d]
                            - self.positions[i][d]
                        )
                        + self.c2
                        * r2
                        * (
                            self.gbest_position[d]
                            - self.positions[i][d]
                        )
                    )

                    self.positions[i][d] += (
                        self.velocities[i][d]
                    )

                    # Keep random keys in [0, 1]
                    self.positions[i][d] = max(
                        0.0,
                        min(
                            1.0,
                            self.positions[i][d]
                        )
                    )

                routes, result = self.evaluate_particle(
                    self.positions[i]
                )

                fitness = result["fitness"]

                # Update personal best
                if fitness < self.pbest_fitness[i]:

                    self.pbest_fitness[i] = fitness

                    self.pbest_positions[i] = (
                        self.positions[i].copy()
                    )

                # Update global best
                if fitness < self.gbest_fitness:

                    self.gbest_fitness = fitness

                    self.gbest_position = (
                        self.positions[i].copy()
                    )

                    self.gbest_routes = routes

            self.history.append(
                self.gbest_fitness
            )

            print(
                f"Iteration {iteration + 1:03d}: "
                f"best fitness = "
                f"{self.gbest_fitness:.6f}"
            )

        return (
            self.gbest_routes,
            self.gbest_fitness,
            self.history
        )


if __name__ == "__main__":

    print("=" * 55)
    print("                 PSO - VRP")
    print("=" * 55)

    # Create network
    network = create_test_network()

    # Create VRP
    problem = create_test_vrp(network)

    # Same heterogeneous traffic used by QPSO
    network.update_traffic("B", "C", 95)
    network.update_traffic("C", "B", 95)

    network.update_traffic("C", "F", 80)
    network.update_traffic("F", "C", 80)

    network.update_traffic("F", "I", 75)
    network.update_traffic("I", "F", 75)

    network.update_traffic("A", "D", 10)
    network.update_traffic("D", "A", 10)

    network.update_traffic("D", "G", 10)
    network.update_traffic("G", "D", 10)

    network.update_traffic("G", "H", 15)
    network.update_traffic("H", "G", 15)

    network.update_traffic("H", "I", 15)
    network.update_traffic("I", "H", 15)

    # Create PSO
    optimizer = PSOVRP(
        problem=problem,
        network=network,
        particles=20,
        iterations=50,
        w=0.7,
        c1=1.5,
        c2=1.5,
    )

    # Run optimization
    best_routes, best_fitness, history = (
        optimizer.optimize()
    )

    print("\nFinal result")
    print("Best routes:", best_routes)
    print("Best fitness:", best_fitness)