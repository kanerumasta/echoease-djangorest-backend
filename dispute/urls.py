from django.urls import path
from .views import ClientDisputeView, ArtistDisputeView, DisputeView, DisputeEvidenceView


urlpatterns = [
    path('client-disputes/', ClientDisputeView.as_view()),
    path('client-disputes/<int:pk>', ClientDisputeView.as_view()),
    path('artist-disputes/', ArtistDisputeView.as_view()),
    path('artist-disputes/<int:pk>', ArtistDisputeView.as_view()),
    path('', DisputeView.as_view()),
    path('evidences', DisputeEvidenceView.as_view()),
]
