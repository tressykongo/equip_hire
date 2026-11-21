
from django.contrib import admin
from .models import (
    Equipment,
    RentalRequest,
    Notification,
    Conversation,
    ChatMessage
)

admin.site.register(Equipment)
admin.site.register(RentalRequest)
admin.site.register(Notification)
admin.site.register(Conversation)
admin.site.register(ChatMessage)
