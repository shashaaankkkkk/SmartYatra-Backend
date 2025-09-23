from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Stop, Route, RouteStop, Bus, Journey, Ticket
from .serializers import (
    StopSerializer, RouteSerializer, RouteCreateSerializer,
    BusSerializer, TicketSerializer, TicketListSerializer, StopETA
)
from geopy.distance import geodesic
from collections import deque

class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    permission_classes = [IsAuthenticated]

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RouteCreateSerializer
        return RouteSerializer

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated]

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketListSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def stop_eta(self, request, pk=None):
        journey = self.get_object()
        stops = journey.route.routestops.all().order_by('order')
        eta_list = []
        current_lat = journey.current_latitude
        current_lon = journey.current_longitude
        current_speed = journey.current_speed or 0.0

        for rs in stops:
            if current_lat is None or current_lon is None or current_speed == 0:
                eta = None
            else:
                distance_km = geodesic((current_lat, current_lon), (rs.stop.latitude, rs.stop.longitude)).km
                eta = int((distance_km / current_speed) * 60)
            eta_list.append({"stop_name": rs.stop.name, "eta_minutes": eta})

        serializer = StopETA(eta_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FindJourneyView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def find_path(self, request):
        start_stop_id = request.query_params.get('start_stop')
        end_stop_id = request.query_params.get('end_stop')

        if not start_stop_id or not end_stop_id:
            return Response({"error": "start_stop and end_stop are required"}, status=400)

        path = self._find_journey_path(int(start_stop_id), int(end_stop_id))
        if not path:
            return Response({"message": "No available path found"}, status=404)

        result = []
        for src, dest, route_id, bus_id in path:
            route = Route.objects.get(id=route_id)
            bus = Bus.objects.get(id=bus_id)
            result.append({
                "from_stop_id": src,
                "to_stop_id": dest,
                "route": route.name,
                "bus_number": bus.bus_number
            })
        return Response({"journey_path": result})

    def _find_journey_path(self, start_stop_id, end_stop_id):
        graph = {}
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
                return path
            visited.add(current)
            for neighbor, route_id, bus_id in graph.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [(current, neighbor, route_id, bus_id)]))
        return None
