from rest_framework import serializers
from django.db import transaction
import qrcode, base64
from io import BytesIO

from .models import Stop, Route, RouteStop, Bus, Ticket


# ---------------- Stop Serializer ----------------
class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'code']


# ---------------- RouteStop Serializer ----------------
class RouteStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer()

    class Meta:
        model = RouteStop
        fields = ['id', 'stop', 'order']


# ---------------- Bus Serializer ----------------
class BusSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = ['id', 'number', 'capacity', 'is_active', 'available_seats']

    def get_available_seats(self, obj):
        return obj.capacity - obj.tickets.count()


# ---------------- Route Serializer ----------------
class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    routestops = RouteStopSerializer(many=True, read_only=True)
    buses = BusSerializer(many=True, read_only=True)  # show buses for route

    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'stops', 'routestops', 'buses']


# ---------------- Route Create Serializer ----------------
class RouteCreateSerializer(serializers.ModelSerializer):
    # Accept stops_payload = [{"stop_id":1,"order":1},...]
    stops_payload = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

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


# ---------------- Ticket Serializer (Route-based) ----------------
class TicketSerializer(serializers.ModelSerializer):
    route_id = serializers.PrimaryKeyRelatedField(
        source='route', queryset=Route.objects.all(), write_only=True
    )
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'passenger', 'route_id', 'route', 'booked_at', 'is_used', 'used_at']
        read_only_fields = ['id', 'passenger', 'route', 'booked_at', 'is_used', 'used_at']

    def create(self, validated_data):
        user = self.context['request'].user
        route = validated_data['route']
        # No bus assignment here; passenger can take any bus on this route
        return Ticket.objects.create(passenger=user, route=route)


# ---------------- Ticket List Serializer (for listing / QR) ----------------
class TicketListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'route', 'booked_at', 'is_used', 'used_at', 'qr_code']

    def get_qr_code(self, obj):
        # QR contains ticket ID and route ID
        data = f"TicketID:{obj.id}|Route:{obj.route.id}|BookedAt:{obj.booked_at}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
