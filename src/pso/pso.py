import random
import  math
class Particle:
    def __init__(self, dimensions, lower_bound, upper_bound):
        self.position = [
            random.uniform(lower_bound, upper_bound)
            for _ in range(dimensions)
        ]

        self.velocity = [
            random.uniform(
                -(upper_bound - lower_bound),
                upper_bound - lower_bound
            )
            for _ in range(dimensions)
        ]

        self.best_position = self.position.copy()
        self.best_value = float("inf")


class PSO:
    def __init__(
        self,
        objective_function,
        dimensions,
        number_of_particles=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
        inertia=0.7,
        cognitive=1.5,
        social=1.5,
    ):
        self.objective_function = objective_function
        self.dimensions = dimensions
        self.number_of_particles = number_of_particles
        self.iterations = iterations

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self.inertia = inertia
        self.cognitive = cognitive
        self.social = social

        self.particles = [
            Particle(
                dimensions,
                lower_bound,
                upper_bound
            )
            for _ in range(number_of_particles)
        ]

        self.global_best_position = None
        self.global_best_value = float("inf")

    def initialize(self):
        """Evaluate the initial particle positions."""

        for particle in self.particles:

            value = self.objective_function(
                particle.position
            )

            particle.best_value = value

            if value < self.global_best_value:

                self.global_best_value = value

                self.global_best_position = (
                    particle.position.copy()
                )

    def update_particle(self, particle):
        """Update one particle."""

        for dimension in range(self.dimensions):

            r1 = random.random()
            r2 = random.random()

            # Velocity update
            particle.velocity[dimension] = (
                self.inertia
                * particle.velocity[dimension]

                + self.cognitive
                * r1
                * (
                    particle.best_position[dimension]
                    - particle.position[dimension]
                )

                + self.social
                * r2
                * (
                    self.global_best_position[dimension]
                    - particle.position[dimension]
                )
            )

            # Position update
            particle.position[dimension] += (
                particle.velocity[dimension]
            )

            # Boundary handling
            particle.position[dimension] = max(
                self.lower_bound,
                min(
                    self.upper_bound,
                    particle.position[dimension]
                )
            )

    def optimize(self,verbose=True):
        """Run the PSO algorithm."""

        self.initialize()

        history = []

        for iteration in range(self.iterations):

            for particle in self.particles:

                self.update_particle(particle)

                value = self.objective_function(
                    particle.position
                )

                # Personal best
                if value < particle.best_value:

                    particle.best_value = value

                    particle.best_position = (
                        particle.position.copy()
                    )

                # Global best
                if value < self.global_best_value:

                    self.global_best_value = value

                    self.global_best_position = (
                        particle.position.copy()
                    )

            history.append(self.global_best_value)

            if verbose:
                print(
                    f"Iteration {iteration + 1:03d}: "
                    f"best = {self.global_best_value:.10f}"
                )

        return (
            self.global_best_position,
            self.global_best_value,
            history
        )


# ---------------------------------------------------------
# Rastrigin benchmark
# ---------------------------------------------------------

def rastrigin(position):
    n = len(position)
    return 10 * n + sum(
        x ** 2 - 10 * math.cos(2 * math.pi * x)
        for x in position
    )

    


# ---------------------------------------------------------
# Run experiment
# ---------------------------------------------------------

if __name__ == "__main__":

    optimizer = PSO(
        objective_function=rastrigin,
        dimensions=5,
        number_of_particles=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
    )

    best_position, best_value, history = (
        optimizer.optimize()
    )

    print("\nFinal result")
    print("Best position:", best_position)
    print("Best fitness:", best_value)