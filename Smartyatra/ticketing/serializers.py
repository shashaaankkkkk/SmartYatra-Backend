from rest_framework import serializers
from django.db import transaction
import qrcode, base64
from io import BytesIO
from django.conf import settings
from .models import Stop, Route, RouteStop, Bus, Journey, Ticket

# ---------------- Stop Serializer ----------------
class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'code', 'latitude', 'longitude']

# ---------------- RouteStop Serializer ----------------
class RouteStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer(read_only=True)

    class Meta:
        model = RouteStop
        fields = ['id', 'stop', 'order']

class JourneySerializer(serializers.ModelSerializer):
    bus = serializers.StringRelatedField(read_only=True)  # shows bus number
    route = serializers.StringRelatedField(read_only=True)  # shows route name
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        source='route',
        write_only=True
    )
    bus_id = serializers.PrimaryKeyRelatedField(
        queryset=Bus.objects.all(),
        source='bus',
        write_only=True
    )

    class Meta:
        model = Journey
        fields = [
            'id',
            'bus', 'bus_id',
            'route', 'route_id',
            'departure_time', 'arrival_time',
            'current_latitude', 'current_longitude',
            'current_speed', 'last_updated'
        ]

class BusSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        source='route',
        write_only=True
    )
    route = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bus
        fields = [
            'id', 'route_id', 'route', 'capacity',
            'available_seats', 'current_latitude', 'current_longitude',
            'current_speed', 'last_updated'
        ]

    def get_available_seats(self, obj):
        # Count tickets of the first journey if exists
        if obj.journeys.exists():
            journey = obj.journeys.first()
            return obj.capacity - journey.tickets.count()
        return obj.capacity

# ---------------- Route Serializer ----------------
class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    routestops = RouteStopSerializer(many=True, read_only=True)
    buses = BusSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'stops', 'routestops', 'buses']

# ---------------- Route Create Serializer ----------------
class RouteCreateSerializer(serializers.ModelSerializer):
    stops_payload = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'stops_payload']

    def create(self, validated_data):
        stops_payload = validated_data.pop('stops_payload', [])
        with transaction.atomic():
            route = Route.objects.create(**validated_data)
            for item in stops_payload:
                stop_id = item.get('stop_id')
                order = item.get('order')
                if stop_id is None or order is None:
                    continue
                route.routestops.create(stop_id=stop_id, order=order)
        return route

# ---------------- Ticket Serializer ----------------
class TicketSerializer(serializers.ModelSerializer):
    route_id = serializers.PrimaryKeyRelatedField(
        source='route', queryset=Route.objects.all(), write_only=True
    )
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'passenger', 'route_id', 'route',
                  'origin_stop', 'destination_stop', 'booked_at', 'is_used', 'used_at']
        read_only_fields = ['id', 'passenger', 'route', 'booked_at', 'is_used', 'used_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return Ticket.objects.create(passenger=user, **validated_data)

# ---------------- Ticket List Serializer (for listing / QR) ----------------
class TicketListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'route', 'origin_stop', 'destination_stop',
                  'booked_at', 'is_used', 'used_at', 'qr_code']

    def get_qr_code(self, obj):
        data = f"TicketID:{obj.id}|Route:{obj.route.id}|Origin:{obj.origin_stop.id}|Destination:{obj.destination_stop.id}|BookedAt:{obj.booked_at}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

# ---------------- Stop ETA Serializer ----------------
class StopETA(serializers.Serializer):
    stop_name = serializers.CharField()
    eta_minutes = serializers.IntegerField()
