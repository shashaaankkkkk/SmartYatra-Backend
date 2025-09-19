from django.urls import path
from .views import UpdateBusLocationView, GetBusLocationView

urlpatterns = [
    path("bus/<int:bus_id>/update-location/", UpdateBusLocationView.as_view(), name="update_bus_location"),
    path("bus/<int:bus_id>/location/", GetBusLocationView.as_view(), name="get_bus_location"),
]
