from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserAccount, Relationship

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Relationship)