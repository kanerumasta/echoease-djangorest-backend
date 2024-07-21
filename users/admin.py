from django.contrib import admin
from .models import (
    UserAccount,
    Profile
)

class CustomAdminModel(admin.ModelAdmin):
    list_display=['pk', '__str__']

admin.site.register([UserAccount, Profile],CustomAdminModel)
