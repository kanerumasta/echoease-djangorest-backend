



from django.urls import path
from .views import (
    ArtistView,
    ArtistApplicationView,
    GenreView,
    IDTypesView,
    follow,unfollow,PortfolioItemView, PortfolioView,
    RateView,
    ConnectionRequestView,
    ArtistConnectionsView,
    SentConnectionRequestView,
    ReceivedConnectionRequestView,
    ArtistUnavailableDatesView
)

# ARTIST URLS

urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view(), name='get-artist-by-pk'),
    path('slug/<slug:slug>', ArtistView.as_view(), name='get-artist-by-slug'),
    path('applications/', ArtistApplicationView.as_view()),
    path('genres/', GenreView.as_view()),
    path('genres/<int:id>', GenreView.as_view()),
    path('accepted-ids',IDTypesView.as_view()),
    path('accepted-ids/<int:pk>',IDTypesView.as_view()),
    path('follow', follow),
    path('unfollow', unfollow),
    path('portfolio-item',PortfolioItemView.as_view()),
    path('portfolio/<int:artist_id>', PortfolioView.as_view()),
    path('rates', RateView.as_view()),
    path('<int:id>/rates', RateView.as_view()),
    path('connection-requests',ConnectionRequestView.as_view()),
    path('connection-requests/sent',SentConnectionRequestView.as_view()),
    path('connection-requests/received', ReceivedConnectionRequestView.as_view()),
    path('connections', ArtistConnectionsView.as_view()),
    path('<int:id>/unavailable-dates',ArtistUnavailableDatesView.as_view()),


]
