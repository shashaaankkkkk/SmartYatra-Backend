from django.db import models
from django.conf import settings
from django.utils import timezone

class SOSAlert(models.Model):
    bus = models.ForeignKey("ticketing.Bus", on_delete=models.CASCADE, related_name="sos_alerts")
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("Active", "Active"), ("Resolved", "Resolved")],
        default="Active"
    )
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"SOS Alert for Bus {self.bus.id} - {self.status}"
