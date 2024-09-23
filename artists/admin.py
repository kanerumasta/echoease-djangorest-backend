from django.contrib import admin


from .models import (
    ArtistApplication,
    Artist,
    Portfolio,
    PortfolioItem,
    Artist,
    Genre,
    IDType,
    Rate
)


class ArtistApplicationAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'status','created','updated')
    list_filter = ('status',)
    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        for application in queryset:
            if application.status == 'under_review':

                try:
                    artist = Artist.objects.create(
                        user = application.user,
                        fb_link = application.fb_link,
                        instagram = application.instagram,
                        twitter = application.twitter,
                        spotify = application.spotify,
                        youtube = application.youtube,
                        idol = application.idol,
                        years_experience = application.years_experience,
                        bio = application.bio,
                        rate = application.rate
                       

                    )

                    artist.genres.set(application.genres.all())
                    
                    application.status = 'approved'
                    application.save()
                    application.user.role = 'artist'
                    application.user.save()
                except Exception as e:
                    print(e)
                    print('Failed approving artist application')


    def reject_applications(self, request, queryset):
        for application in queryset:
            if application.status == 'under_review':
                application.status = 'rejected'
                application.save()

    approve_applications.short_description = 'Approve selected applications'
    reject_applications.short_description = 'Reject selected applications'

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id','slug','__str__', 'status',)
    actions = ['activate', 'deactivate']

    def activate(self, request,queryset):
        for artist in queryset:
            artist.status = "active"
            artist.save()

    def deactivate(self, request,queryset):
        for artist in queryset:
            artist.status = "inactive"
            artist.save()

    activate.short_description = "Activate selected artists"
    deactivate.short_description = "Deactivate selectted artists"

class GenreAdmin(admin.ModelAdmin):
    list_display = ['__str__','id']
    list_display_links = ('id','__str__')

admin.site.register(ArtistApplication, ArtistApplicationAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Portfolio)
admin.site.register(PortfolioItem)
admin.site.register(IDType)
admin.site.register(Rate)