from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StopViewSet, RouteViewSet, BusViewSet, JourneyViewSet, TicketViewSet

router = DefaultRouter()
router.register('stops', StopViewSet)
router.register('routes', RouteViewSet)
router.register('buses', BusViewSet)
router.register('journeys', JourneyViewSet)
router.register('tickets', TicketViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
