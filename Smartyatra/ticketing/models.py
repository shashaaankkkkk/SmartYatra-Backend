from django.db import models
from django.conf import settings


class Stop(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.code})"


class Route(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    stops = models.ManyToManyField(Stop, through="RouteStop", related_name="routes")

    def __str__(self):
        return self.name


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = [
            ('route', 'stop'),
            ('route', 'order'),
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.route.name} - {self.stop.name} (#{self.order})"


class Bus(models.Model):
    bus_number = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=40)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="buses")
    current_latitude = models.FloatField(blank=True, null=True)
    current_longitude = models.FloatField(blank=True, null=True)
    current_speed = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bus_number



class Journey(models.Model):
    """Represents a bus running on a route at a given time."""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="journeys")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(blank=True, null=True)

    # live tracking
    current_latitude = models.FloatField(blank=True, null=True)
    current_longitude = models.FloatField(blank=True, null=True)
    current_speed = models.FloatField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bus.bus_number} on {self.route.name} ({self.departure_time})"


class Ticket(models.Model):
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tickets',
        on_delete=models.CASCADE
    )
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="tickets")
    origin_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="tickets_as_origin")
    destination_stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="tickets_as_destination")
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.passenger} ({self.origin_stop.code} → {self.destination_stop.code})"

