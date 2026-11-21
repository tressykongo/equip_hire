
from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('add/', views.add_equipment, name='add_equipment'),
    path('edit/<int:pk>/', views.edit_equipment, name='edit_equipment'),
    path('delete/<int:pk>/', views.delete_equipment, name='delete_equipment'),
    path('request/<int:pk>/', views.request_equipment, name='request_equipment'),
    path('my-requests/', views.my_rental_requests, name='my_rental_requests'),

    # Owner rental request management
    path('owner-requests/', views.owner_rental_requests, name='owner_rental_requests'),
    path(
        'owner-requests/<int:pk>/<str:action>/',
        views.update_rental_request,
        name='update_rental_request'
    ),

    # Renter notifications
    path('notifications/', views.renter_notifications, name='renter_notifications'),
    path(
        'notifications/<int:pk>/read/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    # Owner notifications
    path('owner-notifications/', views.owner_notifications, name='owner_notifications'),
    path(
        'owner-notifications/<int:pk>/read/',
        views.mark_owner_notification_read,
        name='mark_owner_notification_read'
    ),

    # In-app messaging
    path('messages/', views.message_inbox, name='message_inbox'),
    path(
        'messages/<int:pk>/',
        views.chat_room,
        name='chat_room'
    ),
    path(
        'messages/<int:pk>/send/',
        views.send_chat_message,
        name='send_chat_message'
    ),
]
