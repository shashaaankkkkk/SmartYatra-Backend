from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils import timezone

from .models import BusLocation, LocationHistory
from .serializers import BusLocationSerializer, LocationUpdateSerializer
from ticketing.models import Bus
from ticketing.permissions import IsConductor, IsAuthority


class UpdateBusLocationView(generics.GenericAPIView):
    serializer_class = LocationUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsConductor]

    def post(self, request, bus_id):
        try:
            bus = Bus.objects.get(id=bus_id, assigned_conductor=request.user)
        except Bus.DoesNotExist:
            return Response({"detail": "Bus not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lat = serializer.validated_data["latitude"]
        lon = serializer.validated_data["longitude"]

        location, _ = BusLocation.objects.update_or_create(
            bus=bus,
            defaults={"latitude": lat, "longitude": lon, "updated_at": timezone.now()}
        )

        LocationHistory.objects.create(bus=bus, latitude=lat, longitude=lon)

        return Response(BusLocationSerializer(location).data, status=status.HTTP_200_OK)


class GetBusLocationView(generics.RetrieveAPIView):
    queryset = BusLocation.objects.select_related("bus")
    serializer_class = BusLocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthority]
    lookup_field = "bus_id"
    lookup_url_kwarg = "bus_id"
