



from django.urls import path
from .views import (
    ArtistView,
    ArtistApplicationView,
    GenreView,
)

# ARTIST URLS

urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view(), name='get-artist-by-pk'),
    path('slug/<slug:slug>', ArtistView.as_view(), name='get-artist-by-slug'),
    path('applications/', ArtistApplicationView.as_view()),
    path('genres/', GenreView.as_view()),
    path('genres/<int:id>', GenreView.as_view()),


    
]
  