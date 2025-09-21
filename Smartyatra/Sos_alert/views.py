from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import SOSAlert,timezone
from .serializers import SOSAlertSerializer

class SOSAlertViewSet(viewsets.ModelViewSet):
    queryset = SOSAlert.objects.all()
    serializer_class = SOSAlertSerializer

    def create(self, request, *args, **kwargs):
        # Automatically attach logged-in user as "triggered_by"
        data = request.data.copy()
        data["triggered_by"] = request.user.id if request.user.is_authenticated else None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # TODO: send notification (push, SMS, email, WebSocket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        # If status changes to resolved, mark resolved_at
        instance = serializer.save()
        if instance.status == "Resolved" and not instance.resolved_at:
            instance.resolved_at = timezone.now()
            instance.save()
