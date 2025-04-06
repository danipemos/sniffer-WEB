from django.urls import path
from . import views

app_name = "monitorize"

urlpatterns = [
    path('', views.home, name='home'),
    path('add-user/', views.add_user, name='add_user'),
    path('add-private-key/', views.add_private_key, name='add_private_key'),
    path('add-device/', views.add_device, name='add_device'),
    path("terminal/<str:hostname>/", views.ssh_terminal_view, name="ssh_terminal"),
    path("devices/", views.device_list, name="device_list"),
    path("devices/<str:hostname>/", views.device_detail, name="device_detail"),
    path("set-credentials/<str:hostname>/", views.set_credentials, name="set_credentials"),
    path("edit_file/<str:hostname>/", views.edit_file, name="edit_file"),
]