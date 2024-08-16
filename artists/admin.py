from django.contrib import admin


from .models import (
    ArtistApplication,
    Artist,
    Portfolio,
    PortfolioItem,
    Artist
)


class ArtistApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')
    list_filter = ('status',)
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        for application in queryset:
            if application.status == 'under_review':
                application.status = 'approved'
                application.save()
                Artist.objects.create(
                    user = application.user,
                    dob = application.dob,
                    gender = application.gender,
                    phone = application.phone,
                    bio = application.bio,
                    street = application.street,
                    brgy = application.brgy,
                    city = application.city,
                    country = application.country,
                    zipcode = application.zipcode,
                    fb_page = application.fb_page,
                    instagram = application.instagram,
                    twitter = application.twitter,
                    fb_profile_link = application.fb_profile_link,
                )
                application.user.role = 'artist'
                application.user.save()
    def reject_applications(self, request, queryset):
        for application in queryset:
            if application.status == 'under_review':
                application.status = 'rejected'
                application.save()

    approve_applications.short_description = 'Approve selected applications'
    reject_applications.short_description = 'Reject selected applications'

admin.site.register(ArtistApplication, ArtistApplicationAdmin)
admin.site.register(Artist)