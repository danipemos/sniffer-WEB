from django.urls import path
from . import views

app_name = "monitorize"

urlpatterns = [
    path('', views.home, name='home'),
    path('add-user/', views.add_user, name='add_user'),
    path('add-private-key/', views.add_private_key, name='add_private_key'),
    path('add-device/', views.add_device, name='add_device'),
    path("devices/", views.device_list, name="devices"),
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
    path("users/", views.users, name="users"),
    path("private_keys/", views.private_keys, name="private_keys"),
    path("private_keys/delete/<str:key_id>/", views.delete_private_key, name="delete_private_key"),
    path("private_keys/public_key/<str:key_id>", views.export_public_key, name="export_public_key"),
    path("users/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    path("users/edit/<int:user_id>/", views.edit_user, name="edit_user"),
    path("devices/delete/<int:device_id>/", views.delete_device, name="delete_device"),
    path("devices/edit/<int:device_id>/", views.edit_device, name="edit_device"),
    path("device/delete_file/<int:file_id>/", views.delete_file, name="delete_file"),
    path('device/<str:hostname>/import_key/<str:key_id>/', views.import_gpg_key_to_device, name='import_gpg_key_to_device'),
]