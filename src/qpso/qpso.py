import math
import random


class Particle:
    def __init__(self, dimensions, lower_bound, upper_bound):

        self.position = [
            random.uniform(lower_bound, upper_bound)
            for _ in range(dimensions)
        ]

        # Personal best
        self.best_position = self.position.copy()
        self.best_value = float("inf")


class QPSO:
    def __init__(
        self,
        objective_function,
        dimensions,
        number_of_particles=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
        alpha=0.75,
    ):

        self.objective_function = objective_function

        self.dimensions = dimensions
        self.number_of_particles = number_of_particles
        self.iterations = iterations

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        # Contraction-expansion coefficient
        self.alpha = alpha

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

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self):

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

    # ---------------------------------------------------------
    # Calculate mbest
    # ---------------------------------------------------------

    def calculate_mbest(self):

        mbest = []

        for dimension in range(self.dimensions):

            mean_position = sum(
                particle.best_position[dimension]
                for particle in self.particles
            ) / self.number_of_particles

            mbest.append(mean_position)

        return mbest

    # ---------------------------------------------------------
    # Update particle
    # ---------------------------------------------------------

    def update_particle(self, particle, mbest):

        for dimension in range(self.dimensions):

            # Random values
            phi = random.random()
            u = random.random()

            # Prevent log(0)
            if u == 0:
                u = 1e-10

            # -------------------------------------------------
            # Local attractor
            # -------------------------------------------------

            attractor = (
                phi * particle.best_position[dimension]
                + (1 - phi)
                * self.global_best_position[dimension]
            )

            # -------------------------------------------------
            # Random direction
            # -------------------------------------------------

            if random.random() < 0.5:
                direction = 1
            else:
                direction = -1

            # -------------------------------------------------
            # QPSO position update
            # -------------------------------------------------

            new_position = (
                attractor
                + direction
                * self.alpha
                * abs(
                    mbest[dimension]
                    - particle.position[dimension]
                )
                * math.log(1 / u)
            )

            # -------------------------------------------------
            # Boundary handling
            # -------------------------------------------------

            new_position = max(
                self.lower_bound,
                min(
                    self.upper_bound,
                    new_position
                )
            )

            particle.position[dimension] = new_position

    # ---------------------------------------------------------
    # Optimization
    # ---------------------------------------------------------

    def optimize(self,verbose=True):

        self.initialize()

        history = []

        for iteration in range(self.iterations):

            # Calculate mean best position
            mbest = self.calculate_mbest()

            # Update every particle
            for particle in self.particles:

                self.update_particle(
                    particle,
                    mbest
                )

                # Evaluate new position
                value = self.objective_function(
                    particle.position
                )

                # -------------------------------------------------
                # Personal best
                # -------------------------------------------------

                if value < particle.best_value:

                    particle.best_value = value

                    particle.best_position = (
                        particle.position.copy()
                    )

                # -------------------------------------------------
                # Global best
                # -------------------------------------------------

                if value < self.global_best_value:

                    self.global_best_value = value

                    self.global_best_position = (
                        particle.position.copy()
                    )

            # Store convergence history
            history.append(
                self.global_best_value
            )

            if verbose:
                print(
                    f"Iteration {iteration + 1:03d}: "
                    f"best = "
                    f"{self.global_best_value:.10f}"
                )

        return (
            self.global_best_position,
            self.global_best_value,
            history
        )


# =============================================================
# Sphere Benchmark Function
# =============================================================

def rastrigin(position):
    n = len(position)
    return 10 * n + sum(
        x ** 2 - 10 * math.cos(2 * math.pi * x)
        for x in position
    )

# =============================================================
# Run Experiment
# =============================================================

if __name__ == "__main__":

    optimizer = QPSO(
        objective_function=rastrigin,
        dimensions=5,
        number_of_particles=30,
        iterations=100,
        lower_bound=-5.12,
        upper_bound=5.12,
        alpha=0.75,
    )

    best_position, best_value, history = (
        optimizer.optimize()
    )

    print("\nFinal result")

    print(
        "Best position:",
        best_position
    )

    print(
        "Best fitness:",
        best_value
    )