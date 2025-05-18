from django.urls import path
from .consumers import SSHConsumer, StatsConsumer, FileConsumer, DeviceListConsumer

websocket_urlpatterns = [
    path('ws/ssh/<str:hostname>/', SSHConsumer.as_asgi()),
    path('ws/stats/<str:hostname>/', StatsConsumer.as_asgi()),
    path('ws/files/<str:hostname>/', FileConsumer.as_asgi()),
    path('ws/devices/', DeviceListConsumer.as_asgi()),
]