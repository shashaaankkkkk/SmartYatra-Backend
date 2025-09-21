from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SOSAlertViewSet

router = DefaultRouter()
router.register("sos", SOSAlertViewSet, basename="sosalert")

urlpatterns = [
    path("api/", include(router.urls)),
]
