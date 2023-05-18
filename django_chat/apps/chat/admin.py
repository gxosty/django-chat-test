from django.contrib import admin

from .models import PrivateChat, ChatMessage

# Register your models here.
admin.site.register(PrivateChat)
admin.site.register(ChatMessage)