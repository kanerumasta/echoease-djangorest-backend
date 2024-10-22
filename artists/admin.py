from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    ArtistApplication,
    Artist,
    Portfolio,
    PortfolioItem,
    Artist,
    Genre,
    IDType,
    Rate,
    ConnectionRequest,
    PortfolioItemMedia,

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
                        stage_name = application.stage_name
                    )

                    artist.genres.set(application.genres.all())

                    portfolio = artist.portfolio # type: ignore

                    portfolio_item = PortfolioItem.objects.create(
                        portfolio=portfolio,
                        title='Sample Videos',
                        description='Sample videos from the artist application',
                        group='portfolio'
                    )

                    # Add sample videos to the portfolio item as media
                    sample_videos = [application.sample_video1, application.sample_video2, application.sample_video3]
                    for index, video in enumerate(sample_videos, start=1):
                        if video:
                            PortfolioItemMedia.objects.create(
                                portfolio_item=portfolio_item,
                                media_type='video',
                                file=video
                            )

                    rates = application.rates.all()
                    for rate in rates:
                        rate.artist = artist
                        rate.save()

                    application.status = 'approved'
                    application.save()
                    application.user.role = 'artist'
                    application.user.save()

                    # Send email to the user notifying them of their approval\
                    subject =  'Echoease Artist Application Approval'
                    message = f'Your artist application has been approved.'
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[application.user.email],
                        fail_silently=True
                        )

                except Exception as e:
                    print(e)
                    print('Failed approving artist application')


    def reject_applications(self, request, queryset):
        for application in queryset:
            if application.status == 'under_review':
                application.status = 'rejected'
                application.save()
                subject =  'Echoease Artist Application Declined'
                message = f'We regret to inform you that your application has been rejected. Thank you for your interest in EchoEase.'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[application.user.email],
                    fail_silently=True
                    )


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

class GeneralAdmin(admin.ModelAdmin):
    list_display = ['id','__str__']
    list_display_links = ('id','__str__')

admin.site.register(ArtistApplication, ArtistApplicationAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GeneralAdmin)
admin.site.register(Portfolio,GeneralAdmin)
admin.site.register(PortfolioItem,GeneralAdmin)
admin.site.register(IDType,GeneralAdmin)
admin.site.register(Rate, GeneralAdmin)
admin.site.register(ConnectionRequest, GeneralAdmin)
admin.site.register(PortfolioItemMedia, GeneralAdmin)
