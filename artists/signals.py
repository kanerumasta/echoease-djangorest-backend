from django.db.models.signals import post_save
from django.dispatch import receiver
from notification.models import Notification
from notification.utils import notify_application_accepted
from django.core.mail import send_mail
from django.conf import settings

from .models import Artist, Portfolio, ArtistApplication, PortfolioItem, PortfolioItemMedia

@receiver(post_save, sender = Artist)
def generate_slug(sender, instance,created, **kwargs):
    if created:
        if not instance.slug:
            try:
                instance.slug = instance.user.full_name.replace(' ','-').lower()
                instance.save()
            except:
                print('ERROR(signals): cant generate slug')


@receiver(post_save, sender = Artist)
def create_portfolio(sender, instance, created, **kwargs):
    if created:
        try:
            Portfolio.objects.create(artist = instance)
        except Exception as e:
            print('Error(signals): failed creating portfolio')


# @receiver(post_save, sender = ArtistApplication)
# def save_artist(sender, instance, created, **kwargs):
#     if created:
#         try:
#             print('SIGNAL CALLED')
#             artist = Artist.objects.create(
#                     user = instance.user,
#                     fb_link = instance.fb_link,
#                     instagram = instance.instagram,
#                     twitter = instance.twitter,
#                     spotify = instance.spotify,
#                     youtube = instance.youtube,
#                     idol = instance.idol,
#                     years_experience = instance.years_experience,
#                     bio = instance.bio,
#                     stage_name = instance.stage_name,
#                     account_holder_name = instance.account_holder_name,
#                     channel_code = instance.channel_code,
#                 )
#             print('Artist Created', artist)
#             print('Account number', instance.account_number)
#             if instance.account_number:
#                 print('setting ACCOUNT NUMBER', instance.account_number)
#                 artist.set_account_number(instance.account_number)
#                 print('Account number saved')
#             genres = instance.genres.all()
#             print('genre without al', instance.genres)
#             print('genres count', len(genres))
#             for gen in genres:
#                 print('aoisuhdf',gen.name)
#             if instance.genres.exists():
#                 artist.genres.set(instance.genres.all())
#             artist.save()
#             portfolio = artist.portfolio # type: ignore


#             print('creating portfolios')
#             portfolio_item = PortfolioItem.objects.create(
#                 portfolio=portfolio,
#                 title='Sample Videos',
#                 description='Sample videos from the artist application',
#                 group='portfolio'
#             )

#             # Add sample videos to the portfolio item as media
#             sample_videos = [instance.sample_video1, instance.sample_video2, instance.sample_video3]
#             for video in sample_videos:
#                 if video:
#                     PortfolioItemMedia.objects.create(
#                         portfolio_item=portfolio_item,
#                         media_type='video',
#                         file=video
#                     )

#             rates = instance.rates.all()
#             for rate in rates:
#                 rate.artist = artist
#                 rate.save()

#             instance.status = 'approved'
#             instance.save()
#             instance.user.role = 'artist'
#             instance.user.save()

#             Notification.objects.create(
#                 user=instance.user,
#                 notification_type="application_accepted",
#                 title=f"Welcome to EchoEase, {instance.user.first_name} {instance.user.last_name}",
#                 description="We’re pleased to inform you that your application has been approved. Congratulations on joining EchoEase as an official Echoee! Your talent is now part of a vibrant community of artists. Start connecting with fans and venues, and showcase your music on a platform designed to elevate your artistry. Welcome aboard!"

#             )




#             # Send email to the user notifying them of their approval\

#             subject =  'Echoease Artist Application Approval'
#             message = f'Your artist application has been approved.'
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.user.email],
#                 fail_silently=True
#                 )

#             notify_application_accepted(user=instance.user)
#         except Exception as e:
#             print(e)
#             print('Failed creating artist')
