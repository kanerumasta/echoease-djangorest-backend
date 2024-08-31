from django.urls import path
from .views import (
    ArtistView,
    follow_artist,
    ArtistApplicationView,
    GenreView,
    get_my_artist_profile
)


urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view(), name='get-artist-by-pk'),
    path('slug/<slug:slug>', ArtistView.as_view(), name='get-artist-by-slug'),
    path('applications/', ArtistApplicationView.as_view()),
    path('follow-artist/', follow_artist),
    path('unfollow-artist/', follow_artist),
    path('my-artist-profile/', get_my_artist_profile),
    path('genres/', GenreView.as_view()),
    path('genres/<int:id>', GenreView.as_view()),
    
]
  