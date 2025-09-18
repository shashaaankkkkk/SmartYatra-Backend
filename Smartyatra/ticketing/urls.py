from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StopViewSet, RouteViewSet, BusViewSet, TicketViewSet, analytics_dashboard
)

router = DefaultRouter()
router.register('stops', StopViewSet, basename='stop')
router.register('routes', RouteViewSet, basename='route')
router.register('buses', BusViewSet, basename='bus')
router.register('tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', analytics_dashboard, name='analytics'),
]
