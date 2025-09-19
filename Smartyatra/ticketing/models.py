from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Stop(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Route(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stops = models.ManyToManyField(Stop, through='RouteStop')

    def __str__(self):
        return self.name


class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='routestops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('route', 'stop')
        ordering = ['order']

    def __str__(self):
        return f"{self.route.name} - {self.order} - {self.stop.code}"

class Bus(models.Model):
    number = models.CharField(max_length=50, unique=True)
    route = models.ForeignKey("Route", on_delete=models.CASCADE, related_name="buses")
    capacity = models.PositiveIntegerField(default=40)
    is_active = models.BooleanField(default=True)
    assigned_conductor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_buses"
    )

    def __str__(self):
        return f"Bus {self.number} ({self.route.name})"


class Ticket(models.Model):
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE, related_name='tickets')  # 👈 new field
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='tickets')
    booked_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.passenger} - {self.bus.number} ({self.route.name})"
