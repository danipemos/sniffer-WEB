from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-user/', views.add_user, name='add_user'),
    path('add-private-key/', views.add_private_key, name='add_private_key'),
    path('add-device/', views.add_device, name='add_device'),
]