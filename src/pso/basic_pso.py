import random


def objective(x):
    """Function we want to minimize."""
    return x ** 2


class Particle:
    def __init__(self):
        self.position = random.uniform(-10, 10)
        self.velocity = random.uniform(-1, 1)

        self.best_position = self.position
        self.best_value = objective(self.position)


def pso(
    number_of_particles=10,
    iterations=50,
    w=0.7,
    c1=1.5,
    c2=1.5,
):
    particles = [
        Particle()
        for _ in range(number_of_particles)
    ]

    global_best_position = min(
        particles,
        key=lambda particle: particle.best_value
    ).best_position

    global_best_value = objective(global_best_position)

    for iteration in range(iterations):

        for particle in particles:

            # Generate random coefficients
            r1 = random.random()
            r2 = random.random()

            # Update velocity
            particle.velocity = (
                w * particle.velocity
                + c1 * r1 * (
                    particle.best_position
                    - particle.position
                )
                + c2 * r2 * (
                    global_best_position
                    - particle.position
                )
            )

            # Update position
            particle.position += particle.velocity

            # Evaluate new position
            value = objective(particle.position)

            # Update personal best
            if value < particle.best_value:
                particle.best_position = particle.position
                particle.best_value = value

            # Update global best
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
    best_position, best_value = pso()

    print("\nFinal result")
    print("Best x:", best_position)
    print("Best f(x):", best_value)