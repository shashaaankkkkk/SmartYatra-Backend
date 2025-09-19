# tracking/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrackingViewSet

router = DefaultRouter()
router.register(r"tracking", TrackingViewSet, basename="tracking")

urlpatterns = [
    path("", include(router.urls)),
]
