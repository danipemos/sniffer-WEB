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
    path("service_status/<str:hostname>/", views.service_status, name="service_status"),
    path("start_service/<str:hostname>/", views.start_service, name="start_service"),
    path("stop_service/<str:hostname>/", views.stop_service, name="stop_service"),
    path('api/stats/<str:hostname>/', views.receive_device_stats, name='receive_device_stats'),
    path("upload-file/<str:hostname>/", views.upload_file, name="upload_file"),
    path("decrypt_zip/", views.decrypt_zip, name="decrypt_zip"),
    path("decrypt_encrypted_file/", views.decrypt_encrypted_file, name="decrypt_encrypted_file"),
]