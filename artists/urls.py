from django.urls import path
from .views import (
    ArtistView,
    follow_artist
)


urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view()),
    path('follow-artist/', follow_artist),
    path('unfollow-artist/', follow_artist),
]