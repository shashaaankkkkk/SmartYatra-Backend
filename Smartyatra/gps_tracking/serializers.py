from rest_framework import serializers
from .models import BusLocation, LocationHistory


class BusLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLocation
        fields = ["bus", "latitude", "longitude", "updated_at"]
        read_only_fields = ["updated_at"]


class LocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
