from django.urls import path
from .consumer import NotificationConsumer
websocket_urlpatterns = [
    path('ws/notification/', NotificationConsumer.as_asgi())
]
