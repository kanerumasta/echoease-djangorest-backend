from django.urls import path
from .views import (
    ReviewsView,
    ArtistReviews
)

urlpatterns = [
    path('', ReviewsView.as_view()),
    path('artist-reviews/<int:artist_id>', ArtistReviews.as_view())
]
