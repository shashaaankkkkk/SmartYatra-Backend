from django.urls import path
from .views import GeminiBusChatAPIView

urlpatterns = [
    path("chat-gemini/", GeminiBusChatAPIView.as_view(), name="chat-gemini"),
]