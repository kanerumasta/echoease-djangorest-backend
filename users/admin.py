from django.contrib import admin
from .models import (
    UserAccount,
    Profile
)

class ProfileAdmin(admin.ModelAdmin):
    list_display=('pk','__str__','gender','phone','province','municipality','brgy','street','zipcode' )
    list_display_links = ('pk', '__str__')

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('pk','__str__','first_name', 'last_name','role','is_active')
    list_display_links = ('__str__',)
    actions = ['suspend','unsuspend']

    def suspend(self, request,queryset):
        for user in queryset:
            user.status = "inactive"
            user.save()

    def unsuspend(self, request, queryset):
        for user in queryset:
            user.status = 'active'
            user.save()

admin.site.register(Profile,ProfileAdmin)
admin.site.register(UserAccount, UserAccountAdmin)
