from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('complete/<int:pk>/', views.complete, name='complete'),
    path('delete/<int:pk>/', views.delete, name='delete'),
    path('health/', views.health_check, name='health_check'),
    path("health/", views.health),
]


