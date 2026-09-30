from src.routing.shortest_path import shortest_path


def get_customer_node(problem, customer_id):
    for customer in problem.customers:
        if customer.customer_id == customer_id:
            return customer.node
    raise ValueError(f"Customer ID {customer_id} does not exist.")


def _resolve_node(problem, value):
    return get_customer_node(problem, value) if isinstance(value, int) else value


def calculate_route_cost(problem, network, route, pathfinder=shortest_path, path_weight="weight"):
    """Calculate a VRP route using the selected traffic-aware pathfinder."""
    total_distance = 0.0
    total_travel_time = 0.0
    road_paths = []

    for current_raw, next_raw in zip(route, route[1:]):
        current = _resolve_node(problem, current_raw)
        next_node = _resolve_node(problem, next_raw)
        path, _ = pathfinder(network, current, next_node, weight=path_weight)
        if path is None:
            raise ValueError(f"No path exists between {current} and {next_node}")
        metrics = network.route_metrics(path)
        total_distance += metrics["distance"]
        total_travel_time += metrics["travel_time"]
        road_paths.append({
            "from": current,
            "to": next_node,
            "path": path,
            "distance": metrics["distance"],
            "travel_time": metrics["travel_time"],
            "congestion": metrics["congestion"],
            "fitness": metrics["fitness"],
        })

    return {
        "distance": total_distance,
        "travel_time": total_travel_time,
        "road_paths": road_paths,
    }


def calculate_solution_cost(problem, network, routes, pathfinder=shortest_path, path_weight="weight"):
    total_distance = 0.0
    total_travel_time = 0.0
    route_results = []
    for route in routes:
        result = calculate_route_cost(problem, network, route, pathfinder, path_weight)
        total_distance += result["distance"]
        total_travel_time += result["travel_time"]
        route_results.append(result)
    return {
        "total_distance": total_distance,
        "total_travel_time": total_travel_time,
        "routes": route_results,
    }
