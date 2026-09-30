import math
import random

from src.quantum.quantum_guidance import quantum_guidance
from src.vrp.decoder import decode_position
from src.vrp.fitness import calculate_fitness


class VRPParticle:
    def __init__(self, dimensions):
        self.position = [
            random.random()
            for _ in range(dimensions)
        ]

        self.best_position = self.position.copy()
        self.best_fitness = float("inf")
        self.best_routes = None


class QPSOVRP:

    def __init__(
        self,
        problem,
        network,
        number_of_particles=20,
        iterations=50,
        alpha=0.75,
        quantum_weight=0.30
    ):

        self.problem = problem
        self.network = network

        self.number_of_particles = number_of_particles
        self.iterations = iterations

        self.alpha = alpha
        self.quantum_weight = quantum_weight

        self.dimensions = len(
            problem.customers
        )

        self.particles = [
            VRPParticle(self.dimensions)
            for _ in range(number_of_particles)
        ]

        self.global_best_position = None
        self.global_best_fitness = float("inf")
        self.global_best_routes = None
        self.global_best_result = None

        self.history = []

    # --------------------------------------------------
    # Evaluate a particle
    # --------------------------------------------------

    def evaluate_particle(self, particle):

        routes = decode_position(
            particle.position,
            self.problem
        )

        result = calculate_fitness(
            self.problem,
            self.network,
            routes
        )

        return routes, result

    # --------------------------------------------------
    # Initialize population
    # --------------------------------------------------

    def initialize(self):

        self.global_best_fitness = float("inf")
        self.global_best_position = None
        self.global_best_routes = None
        self.global_best_result = None

        for particle in self.particles:

            routes, result = self.evaluate_particle(
                particle
            )

            fitness = result["fitness"]

            particle.best_fitness = fitness

            particle.best_position = (
                particle.position.copy()
            )

            particle.best_routes = routes

            if fitness < self.global_best_fitness:

                self.global_best_fitness = fitness

                self.global_best_position = (
                    particle.position.copy()
                )

                self.global_best_routes = [
                    route.copy()
                    for route in routes
                ]

                self.global_best_result = result.copy()

    # --------------------------------------------------
    # Calculate mbest
    # --------------------------------------------------

    def calculate_mbest(self):

        mbest = []

        for dimension in range(
            self.dimensions
        ):

            mean_position = sum(
                particle.best_position[dimension]
                for particle in self.particles
            ) / self.number_of_particles

            mbest.append(
                mean_position
            )

        return mbest

    # --------------------------------------------------
    # Re-evaluate historical memory
    # --------------------------------------------------

    def reevaluate_memory(self):
        """
        Re-evaluate stored personal-best positions
        under the current traffic/network state.

        This is important for dynamic traffic because
        a previously good route may become expensive
        after traffic changes.
        """

        # Re-evaluate every particle's personal best
        for particle in self.particles:

            routes = decode_position(
                particle.best_position,
                self.problem
            )

            result = calculate_fitness(
                self.problem,
                self.network,
                routes
            )

            particle.best_fitness = (
                result["fitness"]
            )

            particle.best_routes = [
                route.copy()
                for route in routes
            ]

        # Find current best particle
        best_particle = min(
            self.particles,
            key=lambda particle:
                particle.best_fitness
        )

        # Rebuild global best
        self.global_best_position = (
            best_particle.best_position.copy()
        )

        self.global_best_fitness = (
            best_particle.best_fitness
        )

        self.global_best_routes = decode_position(
            self.global_best_position,
            self.problem
        )

        self.global_best_result = calculate_fitness(
            self.problem,
            self.network,
            self.global_best_routes
        )

    # --------------------------------------------------
    # Update one particle
    # --------------------------------------------------

    def update_particle(
        self,
        particle,
        mbest,
        quantum_guidance_values
    ):

        for dimension in range(
            self.dimensions
        ):

            # Random coefficient
            phi = random.random()

            # Random number for logarithmic term
            u = random.random()

            if u == 0:
                u = 1e-10

            # ------------------------------------------
            # Quantum-guided global component
            # ------------------------------------------

            quantum_value = (
                quantum_guidance_values[
                    dimension
                ]
            )

            quantum_weight = (
                self.quantum_weight
            )

            classical_weight = (
                1.0 - quantum_weight
            )

            guided_global = (
                classical_weight
                * self.global_best_position[
                    dimension
                ]
                +
                quantum_weight
                * quantum_value
            )

            # ------------------------------------------
            # QPSO local attractor
            # ------------------------------------------

            attractor = (
                phi
                * particle.best_position[
                    dimension
                ]
                +
                (1.0 - phi)
                * guided_global
            )

            # ------------------------------------------
            # Random direction
            # ------------------------------------------

            if random.random() < 0.5:
                direction = 1
            else:
                direction = -1

            # ------------------------------------------
            # QPSO update
            # ------------------------------------------

            new_position = (
                attractor
                +
                direction
                * self.alpha
                * abs(
                    mbest[dimension]
                    -
                    particle.position[
                        dimension
                    ]
                )
                * math.log(1.0 / u)
            )

            # ------------------------------------------
            # Random-key bounds
            # ------------------------------------------

            new_position = max(
                0.0,
                min(
                    1.0,
                    new_position
                )
            )

            particle.position[
                dimension
            ] = new_position

    # --------------------------------------------------
    # One optimization iteration
    # --------------------------------------------------

    def optimize_iteration(
        self,
        quantum_guidance_values
    ):

        # Recalculate mbest from current pbest
        mbest = self.calculate_mbest()

        # Update every particle
        for particle in self.particles:

            self.update_particle(
                particle,
                mbest,
                quantum_guidance_values
            )

        # Evaluate updated particles
        for particle in self.particles:

            routes, result = (
                self.evaluate_particle(
                    particle
                )
            )

            fitness = result["fitness"]

            # ------------------------------------------
            # Update personal best
            # ------------------------------------------

            if fitness < particle.best_fitness:

                particle.best_fitness = fitness

                particle.best_position = (
                    particle.position.copy()
                )

                particle.best_routes = [
                    route.copy()
                    for route in routes
                ]

            # ------------------------------------------
            # Update global best
            # ------------------------------------------

            if fitness < self.global_best_fitness:

                self.global_best_fitness = fitness

                self.global_best_position = (
                    particle.position.copy()
                )

                self.global_best_routes = [
                    route.copy()
                    for route in routes
                ]

                self.global_best_result = (
                    result.copy()
                )

        # Save convergence value
        self.history.append(
            self.global_best_fitness
        )

        return (
            self.global_best_routes,
            self.global_best_fitness,
            self.global_best_result
        )

    # --------------------------------------------------
    # Full optimization
    # --------------------------------------------------

    def optimize(self, verbose=True):

        # ----------------------------------------------
        # Initialize particles
        # ----------------------------------------------

        self.initialize()

        # ----------------------------------------------
        # Optimization iterations
        # ----------------------------------------------

        for iteration in range(
            self.iterations
        ):

            # ------------------------------------------
            # Generate fresh quantum guidance
            # ------------------------------------------

            quantum_guidance_values = (
                quantum_guidance(
                    dimensions=self.dimensions,
                    num_qubits=4,
                    shots=100
                )
            )

            # ------------------------------------------
            # Re-evaluate memory if traffic changed
            # ------------------------------------------

            self.reevaluate_memory()

            # ------------------------------------------
            # Perform QPSO iteration
            # ------------------------------------------

            self.optimize_iteration(
                quantum_guidance_values
            )

            # ------------------------------------------
            # Display progress
            # ------------------------------------------

            if verbose:

                print(
                    f"Iteration "
                    f"{iteration + 1:03d}: "
                    f"best fitness = "
                    f"{self.global_best_fitness:.6f}"
                )

        return (
            self.global_best_routes,
            self.global_best_fitness,
            self.history
        )


# ======================================================
# MAIN TEST
# ======================================================

if __name__ == "__main__":

    from src.transport.graph import (
        create_test_network
    )

    from src.vrp.vrp import (
        create_test_vrp
    )

    # --------------------------------------------------
    # Create transportation network
    # --------------------------------------------------

    network = create_test_network()

    # --------------------------------------------------
    # Create VRP problem
    # --------------------------------------------------

    problem = create_test_vrp(
        network
    )

    # --------------------------------------------------
    # Create heterogeneous traffic conditions
    # --------------------------------------------------

    network.update_traffic(
        "B",
        "C",
        95
    )

    network.update_traffic(
        "C",
        "B",
        95
    )

    network.update_traffic(
        "C",
        "F",
        80
    )

    network.update_traffic(
        "F",
        "C",
        80
    )

    network.update_traffic(
        "F",
        "I",
        75
    )

    network.update_traffic(
        "I",
        "F",
        75
    )

    # --------------------------------------------------
    # Keep alternative corridor relatively uncongested
    # --------------------------------------------------

    network.update_traffic(
        "A",
        "D",
        10
    )

    network.update_traffic(
        "D",
        "A",
        10
    )

    network.update_traffic(
        "D",
        "G",
        10
    )

    network.update_traffic(
        "G",
        "D",
        10
    )

    network.update_traffic(
        "G",
        "H",
        15
    )

    network.update_traffic(
        "H",
        "G",
        15
    )

    network.update_traffic(
        "H",
        "I",
        15
    )

    network.update_traffic(
        "I",
        "H",
        15
    )

    # --------------------------------------------------
    # Create QPSO optimizer
    # --------------------------------------------------

    optimizer = QPSOVRP(
        problem=problem,
        network=network,
        number_of_particles=20,
        iterations=50,
        alpha=0.75,
        quantum_weight=0.30
    )

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    print(
        "=" * 55
    )

    print(
        "      QUANTUM-GUIDED QPSO - VRP"
    )

    print(
        "=" * 55
    )

    # --------------------------------------------------
    # Run optimization
    # --------------------------------------------------

    best_routes, best_fitness, history = (
        optimizer.optimize()
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    print(
        "\nFinal result"
    )

    print(
        "Best routes:",
        best_routes
    )

    print(
        "Best fitness:",
        best_fitness
    )

    # --------------------------------------------------
    # Detailed result
    # --------------------------------------------------

    if optimizer.global_best_result is not None:

        result = optimizer.global_best_result

        print(
            f"Distance       : "
            f"{result['distance']:.6f}"
        )

        print(
            f"Travel time    : "
            f"{result['travel_time']:.6f}"
        )

        print(
            f"Congestion     : "
            f"{result['congestion']:.6f}"
        )

        print(
            f"Penalty        : "
            f"{result['penalty']:.6f}"
        )

        print(
            f"Fitness        : "
            f"{result['fitness']:.6f}"
        )