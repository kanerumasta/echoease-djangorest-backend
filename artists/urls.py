



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
    ArtistFollowersView,

    # DefaultTimeSlotView,
    # TimeslotExceptionView,
    # SpecialTimeslotView,
    PortfolioItemMediaView,
    get_recommended_artists,
    remove_genre,
    add_genre,
    # get_artist_timeslots,
    # reset_date_to_default_time_slots
)

# ARTIST URLS

urlpatterns = [
    path('', ArtistView.as_view()),
    path('<int:pk>', ArtistView.as_view(), name='get-artist-by-pk'),
    path('slug/<slug:slug>', ArtistView.as_view(), name='get-artist-by-slug'),
    path('applications/', ArtistApplicationView.as_view()),
    path('applications/<int:id>', ArtistApplicationView.as_view()),
    path('genres/', GenreView.as_view()),
    path('genres/<int:id>', GenreView.as_view()),
    path('genres/<int:id>/delete', remove_genre),
    path('genres/<int:id>/add', add_genre),
    path('accepted-ids',IDTypesView.as_view()),
    path('accepted-ids/<int:pk>',IDTypesView.as_view()),
    path('follow', follow),
    path('unfollow', unfollow),
    path('portfolio-item',PortfolioItemView.as_view()),
    path('portfolio-item/<int:id>',PortfolioItemView.as_view()),
    path('portfolio/<int:artist_id>', PortfolioView.as_view()),
    path('portfolio-item-media',PortfolioItemMediaView.as_view()),
    path('portfolio-item-media/<int:id>',PortfolioItemMediaView.as_view()),
    path('rates', RateView.as_view()),
    path('rates/<int:id>', RateView.as_view()),
    path('<int:id>/rates', RateView.as_view()),


    path('connection-requests',ConnectionRequestView.as_view()),
    path('connection-requests/<int:id>',ConnectionRequestView.as_view()),
    path('connection-requests/sent',SentConnectionRequestView.as_view()),
    path('connection-requests/received', ReceivedConnectionRequestView.as_view()),
    path('connections', ArtistConnectionsView.as_view()),
    path('get-recommended-artists', get_recommended_artists),
    path('<int:artist_id>/followers', ArtistFollowersView.as_view()),


    # path('<int:artist_id>/unavailable-dates',ArtistUnavailableDatesView.as_view()),
    # path('unavailable-dates',ArtistUnavailableDatesView.as_view()),
    # path('unavailable-dates/<int:id>',ArtistUnavailableDatesView.as_view()),
    # path('my-default-time-slots', DefaultTimeSlotView.as_view()),
    # path('<int:artist_id>/time-slots', get_artist_timeslots),
    # path('time-slot-exceptions',TimeslotExceptionView.as_view()),
    # path('time-slot-exceptions/<str:date>',TimeslotExceptionView.as_view()),
    # path('special-time-slots',SpecialTimeslotView.as_view()),
    # path('special-time-slots/<int:id>',SpecialTimeslotView.as_view()),
    # path('reset-timeslots-for-a-date/<str:date>',reset_date_to_default_time_slots),


]
