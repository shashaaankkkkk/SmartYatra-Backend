from rest_framework import serializers
from django.db import transaction
import qrcode, base64
from io import BytesIO

from .models import Stop, Route, RouteStop, Bus, Ticket



class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'code']


class RouteStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer()

    class Meta:
        model = RouteStop
        fields = ['id', 'stop', 'order']


class BusSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = ['id', 'number', 'capacity', 'is_active', 'available_seats']

    def get_available_seats(self, obj):
        return obj.capacity - obj.tickets.count()


class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    routestops = RouteStopSerializer(many=True, read_only=True)
    buses = BusSerializer(many=True, read_only=True)  # show buses for route

    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'stops', 'routestops', 'buses']



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


class TicketSerializer(serializers.ModelSerializer):
    bus_id = serializers.PrimaryKeyRelatedField(
        source='bus', queryset=Bus.objects.filter(is_active=True), write_only=True
    )
    route = RouteSerializer(read_only=True)
    bus = BusSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'passenger', 'bus_id', 'bus', 'route',
            'booked_at', 'is_used', 'used_at'
        ]
        read_only_fields = ['id', 'passenger', 'route', 'booked_at', 'is_used', 'used_at']

    def create(self, validated_data):
        user = self.context['request'].user
        bus = validated_data['bus']

        # Check if bus is full
        if bus.tickets.count() >= bus.capacity:
            raise serializers.ValidationError("This bus is already full.")

        # Auto-assign route from bus
        validated_data['route'] = bus.route
        return Ticket.objects.create(passenger=user, **validated_data)


# ---------------- Ticket List Serializer (for listing / QR) ----------------
class TicketListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'route', 'bus', 'booked_at', 'is_used', 'used_at', 'qr_code']

    def get_qr_code(self, obj):
        data = f"TicketID:{obj.id}|Route:{obj.route.id}|Bus:{obj.bus.id}|BookedAt:{obj.booked_at}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
