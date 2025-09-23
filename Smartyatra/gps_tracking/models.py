from django.db import models
from django.utils import timezone

class BusLocation(models.Model):
    bus = models.OneToOneField("ticketing.Bus", on_delete=models.CASCADE, related_name="location")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bus} - {self.latitude}, {self.longitude}"


class LocationHistory(models.Model):
    bus = models.ForeignKey("ticketing.Bus", on_delete=models.CASCADE, related_name="location_history")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bus} at {self.recorded_at}"
