from django import views
from django.urls import path
from accounts import views

urlpatterns = [
    path('user_login', views.user_login, name='user_login'),
    path('user_register', views.user_register, name='user_register'),
    path('user_logout', views.user_logout, name='user_logout'),
]