# tracking/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import BusLocation
from .serializers import BusLocationSerializer


class TrackingViewSet(viewsets.ViewSet):
    """
    Handles updating and fetching bus locations.
    """

    @action(detail=True, methods=["post"], url_path=r"(?P<lat>-?\d+(\.\d+)?)/(?P<lon>-?\d+(\.\d+)?)")
    def update_location(self, request, pk=None, lat=None, lon=None):
        """
        Conductor updates location via URL params
        Example: POST /tracking/1/55.8/37.6/
        """
        data = {
            "bus": pk,
            "latitude": lat,
            "longitude": lon,
        }
        serializer = BusLocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Location updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="location")
    def get_location(self, request, pk=None):
        """Passenger fetches latest bus location"""
        try:
            location = BusLocation.objects.filter(bus_id=pk).latest("timestamp")
            serializer = BusLocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BusLocation.DoesNotExist:
            return Response({"detail": "No location found"}, status=status.HTTP_404_NOT_FOUND)
