from django.urls import path
from .views import (
    ReviewsView,
    ArtistReviews,
    ArtistListReview
)

urlpatterns = [
    path('', ReviewsView.as_view()),
    path('artist-reviews/<int:artist_id>', ArtistReviews.as_view()),
    path('feedbacks/<int:artist_id>', ArtistListReview.as_view())
]
