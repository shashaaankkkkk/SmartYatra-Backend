from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# ---------------- Stop ----------------
class Stop(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


# ---------------- Route ----------------
class Route(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    stops = models.ManyToManyField(Stop, through='RouteStop', related_name='routes')

    def __str__(self):
        return self.name


# ---------------- RouteStop ----------------
class RouteStop(models.Model):
    route = models.ForeignKey(Route, related_name='routestops', on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('route', 'stop')
        ordering = ['order']

    def __str__(self):
        return f"{self.route.name} - {self.stop.name} ({self.order})"


# ---------------- Bus ----------------
class Bus(models.Model):
    number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    route = models.ForeignKey(Route, related_name='buses', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.number} ({self.route.name})"


# ---------------- Ticket ----------------
class Ticket(models.Model):
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tickets',
        on_delete=models.CASCADE
    )
    route = models.ForeignKey(Route, related_name='tickets', on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.passenger.username} - {self.route.name}"