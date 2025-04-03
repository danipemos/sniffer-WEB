from django.urls import path
from .consumers import SSHConsumer

websocket_urlpatterns = [
    path('ws/ssh/<int:device_id>/', SSHConsumer.as_asgi()),
]