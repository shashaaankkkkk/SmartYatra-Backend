from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone

from .models import Stop, Route, RouteStop, Bus, Ticket
from .serializers import (
    StopSerializer, RouteSerializer, RouteCreateSerializer,
    BusSerializer, TicketSerializer, TicketListSerializer
)
from .permissions import IsAdmin, IsPassenger, IsConductor, IsAuthority

# Admin: Stops
class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# Admin: Routes
class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.prefetch_related('routestops__stop').all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RouteCreateSerializer
        return RouteSerializer


# Admin: Buses
class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.select_related('route').all()
    serializer_class = BusSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# Tickets
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('route', 'passenger').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketListSerializer
        return TicketSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), IsPassenger()]
        if self.action in ['validate_ticket']:
            return [IsAuthenticated(), IsConductor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'customer':
            return Ticket.objects.filter(passenger=user).order_by('-booked_at')
        return Ticket.objects.all().order_by('-booked_at')

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    @action(detail=True, methods=['post'], url_path='validate')
    def validate_ticket(self, request, pk=None):
        # Conductor validates ticket: mark as used
        try:
            ticket = self.get_object()
        except:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        if ticket.is_used:
            return Response({"detail": "Ticket already used"}, status=status.HTTP_400_BAD_REQUEST)
        ticket.is_used = True
        ticket.used_at = timezone.now()
        ticket.save()
        return Response({"detail": "Ticket validated"}, status=status.HTTP_200_OK)


# Authority: analytics
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAuthority])
def analytics_dashboard(request):
    total_tickets = Ticket.objects.count()
    tickets_used = Ticket.objects.filter(is_used=True).count()
    tickets_by_route = Ticket.objects.values('route__id','route__name').annotate(sold=Count('id')).order_by('-sold')
    buses_active = Bus.objects.filter(is_active=True).count()
    return Response({
        "total_tickets": total_tickets,
        "tickets_used": tickets_used,
        "buses_active": buses_active,
        "tickets_by_route": list(tickets_by_route),
    })
