import math
import random


def objective(x):
    """Function we want to minimize."""
    return x ** 2


class Particle:
    def __init__(self):
        # Initial position
        self.position = random.uniform(-10, 10)

        # Personal best
        self.best_position = self.position
        self.best_value = objective(self.position)


def qpso(
    number_of_particles=10,
    iterations=50,
    alpha=0.75,
):
    # Create particles
    particles = [
        Particle()
        for _ in range(number_of_particles)
    ]

    # Find initial global best
    global_best_particle = min(
        particles,
        key=lambda particle: particle.best_value
    )

    global_best_position = global_best_particle.best_position
    global_best_value = global_best_particle.best_value

    for iteration in range(iterations):

        # ------------------------------------------------
        # 1. Calculate mbest
        # ------------------------------------------------

        mbest = sum(
            particle.best_position
            for particle in particles
        ) / number_of_particles

        # ------------------------------------------------
        # 2. Update every particle
        # ------------------------------------------------

        for particle in particles:

            # Random values
            phi = random.random()
            u = random.random()

            # Avoid log(0)
            if u == 0:
                u = 1e-10

            # ------------------------------------------------
            # 3. Calculate local attractor
            # ------------------------------------------------

            attractor = (
                phi * particle.best_position
                + (1 - phi) * global_best_position
            )

            # ------------------------------------------------
            # 4. Quantum-behaved position update
            # ------------------------------------------------

            direction = 1 if random.random() < 0.5 else -1

            particle.position = (
                attractor
                + direction
                * alpha
                * abs(mbest - particle.position)
                * math.log(1 / u)
            )

            # ------------------------------------------------
            # 5. Evaluate fitness
            # ------------------------------------------------

            value = objective(particle.position)

            # ------------------------------------------------
            # 6. Update personal best
            # ------------------------------------------------

            if value < particle.best_value:
                particle.best_position = particle.position
                particle.best_value = value

            # ------------------------------------------------
            # 7. Update global best
            # ------------------------------------------------

            if value < global_best_value:
                global_best_position = particle.position
                global_best_value = value

        print(
            f"Iteration {iteration + 1:02d}: "
            f"x = {global_best_position:.6f}, "
            f"f(x) = {global_best_value:.6f}"
        )

    return global_best_position, global_best_value


if __name__ == "__main__":

    best_position, best_value = qpso()

    print("\nFinal result")
    print("Best x:", best_position)
    print("Best f(x):", best_value)