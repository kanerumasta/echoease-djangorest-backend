from django.urls import path
from .views import (
    ArtistView,
    follow_artist,
    ArtistApplicationView,
    get_my_artist_profile
)


urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view()),
    path('apply/', ArtistApplicationView.as_view()),
    path('follow-artist/', follow_artist),
    path('unfollow-artist/', follow_artist),
    path('my-artist-profile/', get_my_artist_profile)
]
  