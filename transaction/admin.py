from django.contrib import admin
from .models import Transaction

class GeneralAdmin(admin.ModelAdmin):
    list_display = ('pk', '__str__', 'booking')

admin.site.register(Transaction, GeneralAdmin)
