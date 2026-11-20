
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # User dashboards
    path('renter-dashboard/', views.renter_dashboard, name='renter_dashboard'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
]
