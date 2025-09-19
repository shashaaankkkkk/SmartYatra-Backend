from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.utils import timezone

from .models import Stop, Route, Bus, Ticket
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketListSerializer   # show QR + route/bus
        return TicketSerializer           # for creating tickets

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsPassenger]
        elif self.action == 'validate_ticket':
            permission_classes = [IsAuthenticated, IsConductor]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user
        # passengers should only see their own tickets
        if hasattr(user, "role") and user.role == 'customer':
            return Ticket.objects.filter(passenger=user).select_related(
                "route", "passenger"
            ).order_by("-booked_at")
        # conductors/authorities can see all tickets
        return Ticket.objects.select_related("route", "passenger").order_by("-booked_at")

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    @action(detail=True, methods=['post'], url_path='validate')
    def validate_ticket(self, request, pk=None):
        ticket = self.get_object()

        if ticket.is_used:
            return Response(
                {"detail": "Ticket already used"},
                status=status.HTTP_400_BAD_REQUEST
            )

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
    tickets_by_route = (
        Ticket.objects
        .values('route__id','route__name')
        .annotate(sold=Count('id'))
        .order_by('-sold')
    )
    buses_active = Bus.objects.filter(is_active=True).count()
    return Response({
        "total_tickets": total_tickets,
        "tickets_used": tickets_used,
        "buses_active": buses_active,
        "tickets_by_route": list(tickets_by_route),
    })
