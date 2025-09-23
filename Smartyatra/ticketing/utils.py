# ticketing/utils.py
from collections import deque
from .models import RouteStop, Route, Bus

def find_journey_path(start_stop_id, end_stop_id):
    graph = {}

    # Build graph from RouteStop and Bus
    for route in Route.objects.all():
        stops = list(route.routestops.order_by('order'))
        buses = route.buses.all()
        for i in range(len(stops)-1):
            src = stops[i].stop.id
            dest = stops[i+1].stop.id
            if src not in graph:
                graph[src] = []
            for bus in buses:
                graph[src].append((dest, route.id, bus.id))

    visited = set()
    queue = deque()
    queue.append((start_stop_id, []))  

    while queue:
        current, path = queue.popleft()
        if current == end_stop_id:
            return path  # path = list of (src, dest, route_id, bus_id)
        visited.add(current)
        for neighbor, route_id, bus_id in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [(current, neighbor, route_id, bus_id)]))

    return None
