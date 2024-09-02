from django.contrib import admin
from .models import (
    UserAccount,
    Profile
)

class ProfileAdmin(admin.ModelAdmin):
    list_display=('pk','__str__','gender','phone','province','municipality','brgy','street','zipcode' )
    list_display_links = ('pk', '__str__')

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('pk','__str__','first_name', 'last_name','role','joined')
    list_display_links = ('__str__',)

admin.site.register(Profile,ProfileAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
