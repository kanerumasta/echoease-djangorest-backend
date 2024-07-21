from django.contrib import admin

from .models import (
    Portfolio,
    PortfolioItem,
    Artist
)

class CustomAdminModel(admin.ModelAdmin):
    list_display=['pk', '__str__']

admin.site.register([Portfolio, PortfolioItem,Artist],CustomAdminModel)