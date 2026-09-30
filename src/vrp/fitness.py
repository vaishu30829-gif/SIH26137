from src.routing.shortest_path import shortest_path
from src.vrp.route_cost import calculate_solution_cost, _resolve_node


def calculate_congestion_cost(network, routes, problem, pathfinder=shortest_path, path_weight="weight"):
    used_edges = set()
    for route in routes:
        for current_raw, next_raw in zip(route, route[1:]):
            current = _resolve_node(problem, current_raw)
            next_node = _resolve_node(problem, next_raw)
            path, _ = pathfinder(network, current, next_node, weight=path_weight)
            if path is None:
                raise ValueError(f"No path exists between {current} and {next_node}")
            used_edges.update(zip(path, path[1:]))

    return sum(
        network.get_edge(source, target)["traffic"] / network.get_edge(source, target)["capacity"]
        for source, target in used_edges
    )


def calculate_penalty(problem, routes):
    penalty = 0.0
    for route, vehicle in zip(routes, problem.vehicles):
        customer_ids = [node for node in route if isinstance(node, int)]
        if not problem.check_capacity(customer_ids, vehicle):
            penalty += 1000.0
    if not problem.check_customer_coverage(routes):
        penalty += 1000.0
    if not problem.check_duplicate_customers(routes):
        penalty += 1000.0
    if not problem.check_depot_constraints(routes):
        penalty += 1000.0
    return penalty


def calculate_fitness(
    problem,
    network,
    routes,
    distance_weight=1.0,
    time_weight=10.0,
    congestion_weight=2.0,
    penalty_weight=1.0,
    pathfinder=shortest_path,
    path_weight="weight",
):
    cost = calculate_solution_cost(problem, network, routes, pathfinder, path_weight)
    congestion = calculate_congestion_cost(network, routes, problem, pathfinder, path_weight)
    penalty = calculate_penalty(problem, routes)
    fitness = (
        distance_weight * cost["total_distance"]
        + time_weight * cost["total_travel_time"]
        + congestion_weight * congestion
        + penalty_weight * penalty
    )
    return {
        "distance": cost["total_distance"],
        "travel_time": cost["total_travel_time"],
        "congestion": congestion,
        "penalty": penalty,
        "fitness": fitness,
        "routes": cost["routes"],
    }
