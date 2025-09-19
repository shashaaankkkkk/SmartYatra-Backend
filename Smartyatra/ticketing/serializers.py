from rest_framework import serializers
from .models import Stop, Route, RouteStop, Bus, Ticket
from django.db import transaction
import qrcode , base64
from io import BytesIO
from .serializers import RouteSerializer

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'code']


class RouteStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer()

    class Meta:
        model = RouteStop
        fields = ['id', 'stop', 'order']


class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True, read_only=True)
    routestops = RouteStopSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'description', 'stops', 'routestops']


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


class BusSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(source='route', queryset=Route.objects.all(), write_only=True)

    class Meta:
        model = Bus
        fields = ['id', 'number', 'route', 'route_id', 'capacity', 'is_active']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'passenger', 'route', 'booked_at', 'is_used', 'used_at']
        read_only_fields = ['id', 'passenger', 'booked_at', 'is_used', 'used_at']

    def create(self, validated_data):
        user = self.context['request'].user
        # create ticket for the route for requesting user
        return Ticket.objects.create(passenger=user, **validated_data)


class TicketListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'route', 'booked_at', 'is_used', 'used_at']

    def get_qr_code(self, obj):
        # Encode ticket details or just ticket ID
        data = f"TicketID:{obj.id}|Route:{obj.route.id}|BookedAt:{obj.booked_at}"

        # Generate QR code
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        # Convert to Base64 string
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"