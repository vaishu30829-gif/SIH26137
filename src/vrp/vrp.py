import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)
class Customer:
    def __init__(self, customer_id, node, demand):
        self.customer_id = customer_id
        self.node = node
        self.demand = demand

    def __repr__(self):
        return (
            f"Customer("
            f"id={self.customer_id}, "
            f"node={self.node}, "
            f"demand={self.demand}"
            f")"
        )


class Vehicle:
    def __init__(self, vehicle_id, capacity):
        self.vehicle_id = vehicle_id
        self.capacity = capacity

    def __repr__(self):
        return (
            f"Vehicle("
            f"id={self.vehicle_id}, "
            f"capacity={self.capacity}"
            f")"
        )


class VRPProblem:

    def __init__(
        self,
        network,
        depot,
        customers,
        vehicles
    ):
        self.network = network
        self.depot = depot
        self.customers = customers
        self.vehicles = vehicles

    def total_demand(self, customer_ids):
        customer_map = {
            customer.customer_id: customer
            for customer in self.customers
        }

        return sum(
            customer_map[customer_id].demand
            for customer_id in customer_ids
        )

    def check_capacity(
        self,
        customer_ids,
        vehicle
    ):
        demand = self.total_demand(customer_ids)

        return demand <= vehicle.capacity

    def check_customer_coverage(self, routes):
        visited = []

        for route in routes:
            for customer_id in route:
                if customer_id != self.depot:
                    visited.append(customer_id)

        expected = {
            customer.customer_id
            for customer in self.customers
        }

        return set(visited) == expected

    def check_duplicate_customers(self, routes):
        visited = []

        for route in routes:
            for customer_id in route:
                if customer_id != self.depot:
                    visited.append(customer_id)

        return len(visited) == len(set(visited))

    def check_depot_constraints(self, routes):
        for route in routes:

            if len(route) < 2:
                return False

            if route[0] != self.depot:
                return False

            if route[-1] != self.depot:
                return False

        return True

    def validate_solution(self, routes):

        # Number of routes must not exceed vehicles
        if len(routes) > len(self.vehicles):
            return False

        # Every route must start/end at depot
        if not self.check_depot_constraints(routes):
            return False

        # Every customer must appear exactly once
        if not self.check_customer_coverage(routes):
            return False

        if not self.check_duplicate_customers(routes):
            return False

        # Check vehicle capacity
        for index, route in enumerate(routes):

            customer_ids = [
                customer_id
                for customer_id in route
                if customer_id != self.depot
            ]

            vehicle = self.vehicles[index]

            if not self.check_capacity(
                customer_ids,
                vehicle
            ):
                return False

        return True

    def print_problem(self):

        print("\n========================================")
        print("              VRP PROBLEM")
        print("========================================")

        print(f"Depot: {self.depot}")

        print("\nCustomers:")

        for customer in self.customers:
            print(
                f"Customer {customer.customer_id} | "
                f"Node={customer.node} | "
                f"Demand={customer.demand}"
            )

        print("\nVehicles:")

        for vehicle in self.vehicles:
            print(
                f"Vehicle {vehicle.vehicle_id} | "
                f"Capacity={vehicle.capacity}"
            )


def create_test_vrp(network, num_customers=8):
    """
    Create a scalable VRP test instance.

    num_customers:
        Number of customers to generate.

    The transportation network remains the same.
    Customers are distributed across the available
    non-depot graph nodes.

    Vehicle capacity and vehicle count are scaled
    automatically so that the instance remains feasible.
    """

    available_nodes = [
        node for node in network.nodes
        if node != "A"
    ]

    if num_customers < 1:
        raise ValueError("num_customers must be at least 1")

    customers = []

    for i in range(num_customers):
        customer_id = i + 1

        # Cycle through available network nodes.
        node = available_nodes[i % len(available_nodes)]

        # Alternate demand between 2 and 3.
        demand = 2 if i % 2 == 0 else 3

        customers.append(
            Customer(
                customer_id=customer_id,
                node=node,
                demand=demand
            )
        )

    # Use capacity 10 for scalable instances.
    vehicle_capacity = 10

    total_demand = sum(
        customer.demand
        for customer in customers
    )

    vehicle_count = (
        total_demand + vehicle_capacity - 1
    ) // vehicle_capacity

    vehicles = [
        Vehicle(
            vehicle_id=i + 1,
            capacity=vehicle_capacity
        )
        for i in range(vehicle_count)
    ]

    return VRPProblem(
        network=network,
        depot="A",
        customers=customers,
        vehicles=vehicles
    )
if __name__ == "__main__":
    from src.transport.graph import create_test_network

    network = create_test_network()

    for size in [8, 12, 16, 20]:
        problem = create_test_vrp(
            network,
            num_customers=size
        )

        all_customer_ids = [
            customer.customer_id
            for customer in problem.customers
        ]

        print("\n" + "=" * 50)
        print(f"Customers: {size}")
        print(f"Vehicles: {len(problem.vehicles)}")
        print(
            f"Total demand: "
            f"{problem.total_demand(all_customer_ids)}"
        )
        print(
            f"Total capacity: "
            f"{sum(v.capacity for v in problem.vehicles)}"
        )