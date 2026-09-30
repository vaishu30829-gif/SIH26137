import random


def decode_random_keys(
    position,
    problem
):
    """
    Convert a continuous QPSO position into
    a customer ordering.

    Example:

        position = [0.72, 0.15, 0.91]

        Customer IDs:
        [1, 2, 3]

        Sorted by position:
        2 -> 1 -> 3

        Result:
        [2, 1, 3]
    """

    customer_ids = [
        customer.customer_id
        for customer in problem.customers
    ]

    paired = list(
        zip(position, customer_ids)
    )

    paired.sort(
        key=lambda item: item[0]
    )

    ordering = [
        customer_id
        for _, customer_id in paired
    ]

    return ordering

def split_into_routes(ordering, problem):
    """
    Convert a customer ordering into capacity-feasible vehicle routes.

    Uses backtracking with memoization and symmetry breaking.

    Memoization avoids repeatedly exploring equivalent vehicle-load
    states, while symmetry breaking avoids assigning a customer to
    multiple vehicles that currently have the same load.
    """

    customers = {
        customer.customer_id: customer
        for customer in problem.customers
    }

    vehicle_count = len(problem.vehicles)

    assignments = [[] for _ in range(vehicle_count)]
    loads = [0] * vehicle_count

    # Remember states that have already been proven impossible.
    failed_states = set()

    def assign_customer(index):
        # All customers assigned successfully.
        if index == len(ordering):
            return True

        # Vehicle-load state is enough to describe the remaining
        # capacity possibilities.
        state = (
            index,
            tuple(sorted(loads))
        )

        if state in failed_states:
            return False

        customer_id = ordering[index]
        customer = customers[customer_id]

        # Avoid trying multiple vehicles with identical loads.
        tried_loads = set()

        for vehicle_index, vehicle in enumerate(problem.vehicles):

            current_load = loads[vehicle_index]

            # Symmetry breaking:
            # if another vehicle has the same load, trying this
            # vehicle would produce an equivalent state.
            if current_load in tried_loads:
                continue

            tried_loads.add(current_load)

            if (
                current_load + customer.demand
                <= vehicle.capacity
            ):
                assignments[vehicle_index].append(
                    customer_id
                )

                loads[vehicle_index] += customer.demand

                if assign_customer(index + 1):
                    return True

                # Backtrack
                loads[vehicle_index] -= customer.demand

                assignments[vehicle_index].pop()

        # No assignment from this state worked.
        failed_states.add(state)

        return False

    if not assign_customer(0):
        raise ValueError(
            "No capacity-feasible vehicle assignment exists "
            "for this VRP instance."
        )

    routes = []

    for vehicle_customers in assignments:
        route = [problem.depot]
        route.extend(vehicle_customers)
        route.append(problem.depot)

        routes.append(route)

    return routes
def decode_position(
    position,
    problem
):
    """
    Complete decoder:

        Continuous position
                ↓
        Customer ordering
                ↓
        Vehicle assignment
                ↓
        VRP routes
    """

    ordering = decode_random_keys(
        position,
        problem
    )

    routes = split_into_routes(
        ordering,
        problem
    )

    return routes


if __name__ == "__main__":

    from src.transport.graph import create_test_network
    from src.vrp.vrp import create_test_vrp

    network = create_test_network()

    problem = create_test_vrp(
        network,
        num_customers=20
    )

    ordering = [
        customer.customer_id
        for customer in problem.customers
    ]

    routes = split_into_routes(
        ordering,
        problem
    )

    print("\n20-customer test")
    print("Ordering:", ordering)
    print("Routes:", routes)