from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Stop, Route, RouteStop, Bus, Ticket
from .serializers import (
    StopSerializer, RouteSerializer, RouteCreateSerializer,
    BusSerializer, TicketSerializer, TicketListSerializer
)

# ---------------- Stop ViewSet ----------------
class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


# ---------------- Route ViewSet ----------------
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RouteCreateSerializer
        return RouteSerializer


# ---------------- Bus ViewSet ----------------
class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer


# ---------------- Ticket ViewSet ----------------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketListSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    # ---------------- Ticket Validation ----------------
    @action(detail=False, methods=['post'])
    def validate_ticket(self, request):
        """
        Validate ticket for a scanned bus.
        POST payload: { "ticket_id": 1, "bus_id": 2 }
        """
        ticket_id = request.data.get('ticket_id')
        bus_id = request.data.get('bus_id')

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            bus = Bus.objects.get(id=bus_id, is_active=True)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        except Bus.DoesNotExist:
            return Response({"error": "Bus not found or inactive"}, status=status.HTTP_404_NOT_FOUND)

        # Check if ticket belongs to the bus's route
        if ticket.route != bus.route:
            return Response({"error": "Ticket not valid for this bus"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if ticket is already used
        if ticket.is_used:
            return Response({"error": "Ticket already used"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark ticket as used
        ticket.is_used = True
        ticket.used_at = timezone.now()
        ticket.save()

        return Response({"success": "Ticket validated successfully"})
